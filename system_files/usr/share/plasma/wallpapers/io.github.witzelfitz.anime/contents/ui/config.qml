import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    property alias cfg_PauseWhenCovered: covered.checked
    property alias cfg_Interactive: mouse.checked
    Label { text: "Szenen und Akku-Pause findest du im Witzelfitz Hub unter Atmosphäre."; wrapMode: Text.Wrap; Layout.fillWidth: true }
    CheckBox { id: covered; text: "Bei maximierten Fenstern und Vollbild pausieren" }
    CheckBox { id: mouse; text: "Dezente Maus-Parallaxe" }
}
