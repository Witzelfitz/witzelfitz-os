import QtQuick
import org.kde.plasma.workspace.dbus as DBus

QtObject {
    id: root
    property var state: ({theme: "aurora", motion: true, pauseOnBattery: true, scenes: [], onBattery: false, locked: false, track: "", artist: "", profiles: [], rgb: false})
    property string error: ""
    property bool connected: false
    property var props: DBus.Properties {
        service: "io.github.witzelfitz.Desktop"
        path: "/io/github/witzelfitz/Desktop"
        iface: "io.github.witzelfitz.Desktop"
    }
    property var watcher: DBus.DBusServiceWatcher {
        watchedService: "io.github.witzelfitz.Desktop"
        onRegisteredChanged: { if (registered) root.props.updateAll(); }
    }
    property string snapshot: props.properties.Snapshot || ""
    onSnapshotChanged: {
        try { if (snapshot) { state = JSON.parse(snapshot); connected = true; } }
        catch (e) { error = "Desktop-Daten konnten nicht gelesen werden."; }
    }
    Component.onCompleted: {
        // Calling a method also activates the session service on a cold login.
        DBus.SessionBus.asyncCall({service: "io.github.witzelfitz.Desktop",
            path: "/io/github/witzelfitz/Desktop", iface: "org.freedesktop.DBus.Properties",
            member: "GetAll", arguments: ["io.github.witzelfitz.Desktop"]},
            function(reply) { root.props.updateAll(); },
            function(error) { root.error = "Desktop-Dienst ist nicht erreichbar."; });
    }
    function action(name, parameter) {
        error = "";
        DBus.SessionBus.asyncCall({service: "io.github.witzelfitz.Desktop",
            path: "/io/github/witzelfitz/Desktop", iface: "io.github.witzelfitz.Desktop",
            member: "Action", arguments: [name, parameter || ""]},
            function(reply) { root.error = reply.arguments[0] || ""; },
            function(error) { root.error = error.message || "Aktion fehlgeschlagen."; });
    }
}
