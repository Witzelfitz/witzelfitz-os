import QtQuick
import QtQuick.Controls

Button {
    id: root
    property string title
    property string subtitle
    property string number
    property string iconName
    property color accent: "#b3a2ef"
    property color surface: "#141c2e"
    property bool selected: false
    implicitWidth: 280
    implicitHeight: 96
    hoverEnabled: true
    Accessible.name: title + ". " + subtitle
    background: Rectangle {
        radius: 18
        color: root.selected || root.hovered || root.activeFocus ? Qt.rgba(root.surface.r * 1.25, root.surface.g * 1.25, root.surface.b * 1.25, 0.84) : Qt.rgba(root.surface.r, root.surface.g, root.surface.b, 0.78)
        border.width: 1
        border.color: root.selected || root.activeFocus ? root.accent : "#3543516d"
        Rectangle { x: 0; y: 24; width: 3; height: parent.height - 48; radius: 2; color: root.accent; visible: root.selected }
    }
    contentItem: Item {
        Glyph { x: 15; y: 13; width: 27; height: 27; name: root.iconName; color: root.accent }
        Text { x: 57; y: 9; width: parent.width - 70; text: root.title; color: "#f3f3fa"; font.pixelSize: 18; font.weight: Font.DemiBold; elide: Text.ElideRight }
        Text { x: 57; y: 37; width: parent.width - 70; text: root.subtitle; color: "#a7b2ca"; font.pixelSize: 11; elide: Text.ElideRight }
        Text { anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 9; text: root.number; color: "#68758e"; font.pixelSize: 10; font.letterSpacing: 1.5 }
    }
}
