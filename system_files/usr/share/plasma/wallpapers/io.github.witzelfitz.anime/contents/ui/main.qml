import QtQuick
import org.kde.plasma.plasmoid
import org.kde.taskmanager as TaskManager
import "../../../../../witzelfitz-desktop/qml" as Desktop

WallpaperItem {
    id: root
    Desktop.Bridge { id: bridge }
    property var scene: {
        var list = bridge.state.scenes || [];
        for (var i = 0; i < list.length; ++i) if (list[i].id === bridge.state.theme) return list[i];
        return {image: Qt.resolvedUrl("../../../../../witzelfitz-desktop/wallpapers/konan.png"), accent: "#b3a2ef", effect: "rain"};
    }
    property bool covered: false
    accentColor: scene.accent
    function updateCovered() {
        var blocked = false;
        for (var i = 0; i < windows.count; ++i) {
            var item = windows.objectAt(i);
            if (item && item.covering) { blocked = true; break; }
        }
        covered = blocked;
    }
    TaskManager.TasksModel {
        id: tasks
        filterByCurrentVirtualDesktop: true
        filterMinimized: true
        groupMode: TaskManager.TasksModel.GroupDisabled
    }
    Instantiator {
        id: windows
        model: tasks
        delegate: QtObject {
            required property var model
            property bool covering: !!(model.IsWindow && (model.IsMaximized || model.IsFullScreen))
            onCoveringChanged: Qt.callLater(root.updateCovered)
        }
        onObjectAdded: Qt.callLater(root.updateCovered)
        onObjectRemoved: Qt.callLater(root.updateCovered)
    }
    Desktop.Scene {
        anchors.fill: parent
        imageSource: root.scene.image
        effect: root.scene.effect
        accent: root.scene.accent
        interactive: root.configuration.Interactive
        animate: bridge.connected && bridge.state.motion && !bridge.state.locked
                 && !(bridge.state.onBattery && bridge.state.pauseOnBattery)
                 && !(root.covered && root.configuration.PauseWhenCovered)
    }
}
