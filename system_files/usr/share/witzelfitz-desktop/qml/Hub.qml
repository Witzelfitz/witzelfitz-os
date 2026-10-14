import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var state: ({theme: "aurora", motion: true, pauseOnBattery: true, scenes: [], battery: null, onBattery: false, track: "", artist: "", profiles: [], rgb: false})
    property string error: ""
    property bool connected: false
    property int selected: -1
    property var now: new Date()
    property var scene: {
        var values = state.scenes || [];
        for (var i = 0; i < values.length; ++i) if (values[i].id === state.theme) return values[i];
        return {id: "aurora", name: "Aurora", character: "Aurora", series: "WITZEL OS", accent: "#b3a2ef"};
    }
    property color accent: scene.accent
    property color surface: scene.surface || "#141c2e"
    signal action(string name, string parameter)
    implicitWidth: 680
    implicitHeight: 740
    readonly property var sections: [
        {title: "Games", sub: "Deine Bibliothek. Dein nächstes Abenteuer.", icon: "applications-games"},
        {title: "Workspace", sub: "Projekte, Terminal & Agenten", icon: "folder-development"},
        {title: "Orte", sub: "Alles, was du schnell finden möchtest", icon: "folder"},
        {title: "Sound", sub: "Musik, Geräte & dein Klang", icon: "audio-headphones"},
        {title: "System", sub: "Energie, Verbindung & Kontrolle", icon: "preferences-system"},
        {title: "Atmosphäre", sub: "Ein anderer Ort. Eine andere Stimmung.", icon: "preferences-desktop-wallpaper"}
    ]
    function actionsFor(section) {
        switch(section) {
        case 0: return [
            {label: "Steam", action: "steam", icon: "steam"},
            {label: "Lutris", action: "lutris", icon: "applications-games"},
            {label: "Big Picture", action: "bigpicture", icon: "view-fullscreen"},
            {label: "Games-Ordner", action: "folder", param: "GAMES", icon: "folder"}];
        case 1: return [
            {label: "Terminal", action: "terminal", icon: "utilities-terminal"},
            {label: "Editor", action: "editor", icon: "accessories-text-editor"},
            {label: "Agenten", action: "agents", icon: "system-run"},
            {label: "Projekte", action: "folder", param: "PROJECTS", icon: "folder-development"}];
        case 2: return [
            {label: "Home", action: "folder", param: "HOME", icon: "user-home"},
            {label: "Downloads", action: "folder", param: "DOWNLOAD", icon: "folder-download"},
            {label: "Desktop-Dateien", action: "folder", param: "DESKTOP", icon: "folder"},
            {label: "Dokumente", action: "folder", param: "DOCUMENTS", icon: "folder-documents"},
            {label: "Bilder", action: "folder", param: "PICTURES", icon: "folder-pictures"}];
        case 3: return [
            {label: "Audio-Geräte", action: "kcm", param: "kcm_pulseaudio", icon: "audio-card"},
            {label: "EasyEffects", action: "effects", icon: "audio-volume-high"},
            {label: "Leiser", action: "volume", param: "down", icon: "audio-volume-low"},
            {label: "Lauter", action: "volume", param: "up", icon: "audio-volume-high"},
            {label: "Stumm", action: "volume", param: "mute", icon: "audio-volume-muted"}];
        case 4: return [
            {label: "WLAN", action: "kcm", param: "kcm_networkmanagement", icon: "network-wireless"},
            {label: "Bluetooth", action: "kcm", param: "kcm_bluetooth", icon: "preferences-system-bluetooth"},
            {label: "Energie", action: "kcm", param: "kcm_powerdevilprofilesconfig", icon: "battery"},
            {label: "GPU", action: "gpu", icon: "video-display"},
            {label: "Einstellungen", action: "settings", icon: "preferences-system"}];
        default: return [];
        }
    }
    Timer { interval: 1000; repeat: true; running: root.visible; onTriggered: root.now = new Date() }

    Flickable {
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: body.implicitHeight + 20
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        ColumnLayout {
            id: body
            width: parent.width - 8
            spacing: 16
            RowLayout {
                Layout.fillWidth: true
                Text { text: "W / F"; color: root.accent; font.pixelSize: 15; font.weight: Font.Bold; font.letterSpacing: 3 }
                Rectangle { width: 28; height: 1; color: "#667789a8" }
                Text { visible: root.width > 450; text: "DEIN DESKTOP. DEINE WELT."; color: "#aab6cc"; font.pixelSize: 9; font.letterSpacing: 1.7 }
                Item { Layout.fillWidth: true }
                Rectangle { width: 6; height: 6; radius: 3; color: root.connected ? "#8cceaf" : "#c7a87a" }
            }
            RowLayout {
                Layout.fillWidth: true
                ColumnLayout {
                    spacing: 3
                    Text { text: "Willkommen zurück."; color: "#f1f3fc"; font.pixelSize: root.width < 470 ? 25 : 34; font.weight: Font.DemiBold; font.letterSpacing: -1 }
                    Text { text: root.now.toLocaleDateString(Qt.locale("de_CH"), "dddd, d. MMMM") + "  ·  Witzelfitz OS"; color: "#a3aec5"; font.pixelSize: 12 }
                }
                Item { Layout.fillWidth: true }
                Text { visible: root.width > 530; text: Qt.formatTime(root.now, "HH:mm"); color: "#f0effa"; font.pixelSize: 32; font.weight: Font.Light }
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: "#30404b64" }
            GridLayout {
                Layout.fillWidth: true
                columns: width < 470 ? 1 : 2
                columnSpacing: 12
                rowSpacing: 12
                Repeater {
                    model: root.sections
                    HubCard {
                        required property var modelData
                        required property int index
                        Layout.fillWidth: true
                        title: modelData.title
                        subtitle: index === 3 && root.state.track ? root.state.track : modelData.sub
                        number: "0" + (index + 1)
                        iconName: modelData.icon
                        accent: root.accent; surface: root.surface
                        selected: root.selected === index
                        onClicked: root.selected = root.selected === index ? -1 : index
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: details.implicitHeight + 32
                visible: root.selected >= 0
                radius: 18
                color: Qt.rgba(root.surface.r, root.surface.g, root.surface.b, 0.86)
                border.color: "#3543516d"
                ColumnLayout {
                    id: details
                    x: 16; y: 16; width: parent.width - 32
                    spacing: 12
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: root.selected >= 0 ? root.sections[root.selected].title : ""; color: root.accent; font.pixelSize: 13; font.weight: Font.DemiBold }
                        Item { Layout.fillWidth: true }
                        ActionButton { text: "Schliessen"; accent: root.accent; surface: root.surface; implicitHeight: 28; onClicked: root.selected = -1 }
                    }
                    Text {
                        visible: root.selected === 3 && !!root.state.track
                        text: root.state.track + (root.state.artist ? " · " + root.state.artist : "")
                        color: "#d5dcec"; font.pixelSize: 12; elide: Text.ElideRight; Layout.fillWidth: true
                    }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 8
                        Repeater {
                            model: root.actionsFor(root.selected)
                            ActionButton {
                                required property var modelData
                                text: modelData.label; iconName: modelData.icon || ""; accent: root.accent; surface: root.surface
                                onClicked: root.action(modelData.action, modelData.param || "")
                            }
                        }
                        Repeater {
                            model: root.selected === 3 ? [
                                {label: "Zurück", param: "Previous"},
                                {label: root.state.playing ? "Pause" : "Play", param: "PlayPause"},
                                {label: "Weiter", param: "Next"}] : []
                            ActionButton {
                                required property var modelData
                                text: modelData.label; accent: root.accent; surface: root.surface; enabled: !!root.state.track
                                onClicked: root.action("media", modelData.param)
                            }
                        }
                        Repeater {
                            model: root.selected === 4 ? root.state.profiles || [] : []
                            ActionButton {
                                required property string modelData
                                text: ({"power-saver":"Sparsam", "balanced":"Ausgewogen", "performance":"Leistung"})[modelData] || modelData
                                accent: root.accent; surface: root.surface; selected: root.state.profile === modelData
                                onClicked: root.action("profile", modelData)
                            }
                        }
                    }
                    Flow {
                        visible: root.selected === 5
                        Layout.fillWidth: true
                        spacing: 8
                        Repeater {
                            model: root.state.scenes || []
                            ActionButton {
                                required property var modelData
                                text: modelData.character; accent: modelData.accent; surface: root.surface; selected: root.state.theme === modelData.id
                                onClicked: root.action("theme", modelData.id)
                            }
                        }
                    }
                    RowLayout {
                        visible: root.selected === 5
                        Layout.fillWidth: true
                        ActionButton { text: root.state.motion ? "Animation: an" : "Animation: aus"; accent: root.accent; surface: root.surface; selected: root.state.motion; onClicked: root.action("motion", root.state.motion ? "false" : "true") }
                        ActionButton { text: "Akku-Pause"; accent: root.accent; surface: root.surface; selected: root.state.pauseOnBattery; onClicked: root.action("pauseOnBattery", root.state.pauseOnBattery ? "false" : "true") }
                    }
                    Flow {
                        visible: root.selected === 5
                        ActionButton { text: "Szenen verwalten …"; accent: root.accent; surface: root.surface; onClicked: root.action("manager", "") }
                    }
                    Flow {
                        visible: root.selected === 5 && root.state.rgb
                        Layout.fillWidth: true; spacing: 8
                        Repeater {
                            model: [{label:"Tastatur koppeln", key:"syncKeyboard"}, {label:"KDE-Farben koppeln", key:"syncColors"}]
                            ActionButton {
                                required property var modelData
                                text: modelData.label; accent: root.accent; surface: root.surface; selected: !!root.state[modelData.key]
                                onClicked: root.action(modelData.key, root.state[modelData.key] ? "false" : "true")
                            }
                        }
                        Text { text: root.scene.paletteName || "Individuell"; color: root.accent; font.pixelSize: 11; height: 38; verticalAlignment: Text.AlignVCenter }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                height: 70
                radius: 16
                color: Qt.rgba(root.surface.r, root.surface.g, root.surface.b, 0.7)
                border.color: "#3043516d"
                RowLayout {
                    anchors.fill: parent; anchors.margins: 15; spacing: 14
                    Rectangle { width: 3; height: 28; radius: 2; color: root.accent }
                    ColumnLayout {
                        spacing: 3
                        Text { text: root.scene.series + "  /  " + root.scene.character; color: root.accent; font.pixelSize: 9; font.letterSpacing: 1.3 }
                        Text { text: root.scene.name; color: "#edf0f9"; font.pixelSize: 17; font.weight: Font.DemiBold }
                    }
                    Item { Layout.fillWidth: true }
                    ColumnLayout {
                        spacing: 4
                        Text { text: root.state.battery === null || root.state.battery === undefined ? "" : root.state.battery + "% AKKU"; color: "#c4cde0"; font.pixelSize: 10; Layout.alignment: Qt.AlignRight }
                        Text { text: root.state.onBattery && root.state.pauseOnBattery ? "RUHEMODUS" : root.state.motion ? "LIVE ATMOSPHERE" : "STILL"; color: "#8695b1"; font.pixelSize: 9; font.letterSpacing: 1; Layout.alignment: Qt.AlignRight }
                    }
                }
            }
            Text { visible: !!root.error || !!root.state.appearanceError; text: root.error || root.state.appearanceError || ""; color: "#ffb6be"; font.pixelSize: 12; wrapMode: Text.Wrap; Layout.fillWidth: true }
            Text { text: "Wähle einen Bereich, um deine Aktionen zu öffnen."; color: "#8491ac"; font.pixelSize: 10 }
        }
    }
}
