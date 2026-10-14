import QtQuick

Canvas {
    id: root
    property string name: ""
    property color color: "#b3a2ef"
    onColorChanged: requestPaint()
    onNameChanged: requestPaint()
    onPaint: {
        var c = getContext("2d"); c.reset();
        c.scale(width / 28, height / 28);
        c.strokeStyle = root.color.toString(); c.lineWidth = 1.6; c.lineCap = "round"; c.lineJoin = "round";
        c.beginPath();
        if (name === "applications-games") {
            c.moveTo(8, 8); c.lineTo(20, 8); c.bezierCurveTo(25, 8, 28, 24, 23, 23);
            c.lineTo(18, 19); c.lineTo(10, 19); c.lineTo(5, 23); c.bezierCurveTo(0, 24, 3, 8, 8, 8);
            c.moveTo(7, 12); c.lineTo(7, 18); c.moveTo(4, 15); c.lineTo(10, 15);
            c.moveTo(19, 13); c.lineTo(19.1, 13); c.moveTo(22, 16); c.lineTo(22.1, 16);
        } else if (name === "folder-development" || name === "utilities-terminal") {
            c.rect(3, 5, 22, 18); c.moveTo(7, 10); c.lineTo(11, 14); c.lineTo(7, 18); c.moveTo(15, 18); c.lineTo(21, 18);
        } else if (name.indexOf("folder") >= 0 || name === "user-home") {
            c.moveTo(3, 9); c.lineTo(3, 6); c.lineTo(11, 6); c.lineTo(14, 9); c.lineTo(25, 9); c.lineTo(25, 23); c.lineTo(3, 23); c.closePath();
        } else if (name.indexOf("audio") >= 0) {
            c.moveTo(4, 17); c.lineTo(4, 14); c.arc(14, 14, 10, Math.PI, 0); c.lineTo(24, 20);
            c.rect(3, 16, 5, 8); c.rect(20, 16, 5, 8);
        } else if (name === "preferences-system") {
            c.arc(14, 14, 6, 0, Math.PI * 2);
            for (var i=0; i<8; ++i) { var a=i*Math.PI/4; c.moveTo(14+Math.cos(a)*9,14+Math.sin(a)*9); c.lineTo(14+Math.cos(a)*12,14+Math.sin(a)*12); }
        } else if (name === "preferences-desktop-wallpaper") {
            c.moveTo(20, 6); c.bezierCurveTo(2, 0, 0, 25, 19, 24); c.bezierCurveTo(9, 19, 10, 11, 20, 6);
            c.moveTo(23, 3); c.lineTo(23, 9); c.moveTo(20, 6); c.lineTo(26, 6);
        } else {
            c.moveTo(10, 6); c.lineTo(18, 14); c.lineTo(10, 22);
        }
        c.stroke();
    }
}
