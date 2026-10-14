import QtQuick
import QtQuick.Controls

Button {
    id: root
    property color accent: "#b3a2ef"
    property color surface: "#141c2e"
    property bool selected: false
    property string iconName: ""
    implicitHeight: 38
    implicitWidth: contentItem.implicitWidth + 26
    hoverEnabled: true
    Accessible.name: text
    background: Rectangle {
        radius: 10
        color: root.selected || root.down || root.hovered || root.activeFocus ? Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.17) : Qt.rgba(root.surface.r, root.surface.g, root.surface.b, 0.3)
        border.width: 1
        border.color: root.selected || root.activeFocus ? root.accent : "#253f4b68"
    }
    contentItem: Row {
        spacing: 7
        Glyph { width: root.iconName ? 17 : 0; height: 17; anchors.verticalCenter: parent.verticalCenter; name: root.iconName; color: root.accent }
        Text { text: root.text; color: root.enabled ? "#e9ebf5" : "#737d96"; font.pixelSize: 12; anchors.verticalCenter: parent.verticalCenter }
    }
    ToolTip.visible: hovered && !enabled
    ToolTip.text: "Auf diesem System nicht verfügbar"
}
