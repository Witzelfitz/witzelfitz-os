import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import "../../../../../witzelfitz-desktop/qml" as Desktop

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    Layout.minimumWidth: 360
    Layout.minimumHeight: 430
    Layout.preferredWidth: 680
    Layout.preferredHeight: 740
    preferredRepresentation: fullRepresentation
    Desktop.Bridge { id: bridge }
    fullRepresentation: Desktop.Hub {
        state: bridge.state
        error: bridge.error
        connected: bridge.connected
        onAction: (name, parameter) => bridge.action(name, parameter)
    }
}
