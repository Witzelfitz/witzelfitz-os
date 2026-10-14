import QtQuick

Item {
    id: root
    property url imageSource
    property string effect: "rain"
    property color accent: "#b3a2ef"
    property bool animate: true
    property bool interactive: true
    property real phase: 0
    property real pointerX: 0
    property real pointerY: 0
    clip: true

    Rectangle { anchors.fill: parent; color: "#101524" }
    Image {
        id: artwork
        x: -12 + root.pointerX * 6
        y: -12 + root.pointerY * 4
        width: root.width + 24
        height: root.height + 24
        source: root.imageSource
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: true
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: "#36101524" }
            GradientStop { position: 0.55; color: "#00101524" }
            GradientStop { position: 1; color: "#12101524" }
        }
    }
    Canvas {
        id: atmosphere
        anchors.fill: parent
        visible: root.animate && root.effect !== "none"
        renderStrategy: Canvas.Cooperative
        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            var t = root.phase;
            if (root.effect === "rain") {
                ctx.strokeStyle = "rgba(190,203,235,0.17)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                for (var i = 0; i < 65; ++i) {
                    var x = (i * 157.7 + t * 32) % (width + 100) - 50;
                    var y = (i * 91.3 + t * (135 + i % 5 * 22)) % (height + 80) - 40;
                    ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 24);
                }
                ctx.stroke();
                ctx.fillStyle = "rgba(224,220,249,0.28)";
                for (var j = 0; j < 9; ++j) {
                    var px = (j * 211 + t * 13) % (width + 70) - 35;
                    var py = height * (0.2 + j / 14) + Math.sin(t * 0.7 + j) * 25;
                    ctx.save(); ctx.translate(px, py); ctx.rotate(Math.sin(t * 0.35 + j) * 0.6);
                    ctx.beginPath(); ctx.moveTo(0, -5); ctx.lineTo(10, 0); ctx.lineTo(0, 7); ctx.lineTo(-9, 0); ctx.closePath(); ctx.fill(); ctx.restore();
                }
            } else if (root.effect === "ocean") {
                ctx.strokeStyle = "rgba(237,187,134,0.13)";
                ctx.lineWidth = 1.5;
                for (var row = 0; row < 12; ++row) {
                    ctx.beginPath();
                    for (var sx = 0; sx <= width * 0.6; sx += 22) {
                        var sy = height * 0.65 + row * 22 + Math.sin(sx / 85 + t * 0.8 + row) * 4;
                        if (sx === 0) ctx.moveTo(sx, sy); else ctx.lineTo(sx, sy);
                    }
                    ctx.stroke();
                }
            } else if (root.effect === "threads") {
                ctx.strokeStyle = "rgba(234,160,199,0.16)";
                ctx.lineWidth = 1;
                for (var line = 0; line < 6; ++line) {
                    ctx.beginPath();
                    ctx.moveTo(width * 0.45, height * 0.7 + line * 12);
                    ctx.bezierCurveTo(width * 0.6, height * (0.3 + Math.sin(t * 0.3 + line) * 0.05),
                        width * 0.8, height * 0.75, width, height * (0.25 + line * 0.06));
                    ctx.stroke();
                }
            } else if (root.effect === "petals") {
                ctx.fillStyle = "rgba(232,154,173,0.32)";
                for (var petal = 0; petal < 20; ++petal) {
                    var rx = (petal * 177.1 + t * 17) % (width + 60) - 30;
                    var ry = (petal * 103.7 + t * (18 + petal % 4 * 5)) % (height + 60) - 30;
                    ctx.save(); ctx.translate(rx, ry); ctx.rotate(t * 0.18 + petal);
                    ctx.beginPath(); ctx.moveTo(0, -6);
                    ctx.bezierCurveTo(9, -5, 7, 5, 0, 7);
                    ctx.bezierCurveTo(-7, 5, -3, -4, 0, -6);
                    ctx.fill(); ctx.restore();
                }
            } else if (root.effect === "fireflies") {
                for (var fly = 0; fly < 32; ++fly) {
                    var fx = width * ((fly * 0.173) % 1) + Math.sin(t * 0.5 + fly) * 17;
                    var fy = height * ((fly * 0.237) % 1) + Math.cos(t * 0.4 + fly * 2) * 22;
                    var alpha = 0.16 + (Math.sin(t * 1.1 + fly) + 1) * 0.18;
                    ctx.fillStyle = "rgba(235,218,255," + alpha + ")";
                    ctx.beginPath(); ctx.arc(fx, fy, 1.4 + fly % 3 * 0.4, 0, Math.PI * 2); ctx.fill();
                    ctx.fillStyle = "rgba(189,168,242," + alpha * 0.17 + ")";
                    ctx.beginPath(); ctx.arc(fx, fy, 5, 0, Math.PI * 2); ctx.fill();
                }
            } else if (root.effect === "steam") {
                ctx.lineWidth = 13;
                ctx.lineCap = "round";
                ctx.strokeStyle = "rgba(215,210,244,0.045)";
                for (var plume = 0; plume < 7; ++plume) {
                    var base = width * (0.08 + plume * 0.09);
                    var lift = (t * 9 + plume * 17) % 90;
                    ctx.beginPath(); ctx.moveTo(base, height * 0.89 - lift);
                    ctx.bezierCurveTo(base - 28, height * 0.77 - lift,
                        base + Math.sin(t * 0.4 + plume) * 35, height * 0.71 - lift,
                        base + 9, height * 0.6 - lift);
                    ctx.stroke();
                }
            }
        }
    }
    Timer {
        interval: 34 // About 29 FPS, independently of a 144 Hz display.
        running: root.animate && root.effect !== "none" && root.visible && root.width > 0
        repeat: true
        onTriggered: { root.phase += 0.034; atmosphere.requestPaint(); }
    }
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton
        hoverEnabled: root.interactive && root.animate
        onPositionChanged: (mouse) => {
            root.pointerX = mouse.x / width * 2 - 1;
            root.pointerY = mouse.y / height * 2 - 1;
        }
        onExited: { root.pointerX = 0; root.pointerY = 0; }
    }
    onAnimateChanged: { if (!animate) { pointerX = 0; pointerY = 0; } }
}
