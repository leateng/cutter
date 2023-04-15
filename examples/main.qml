import QtQuick
import QtQuick.Controls

ApplicationWindow {
  visible: true
  width: 600
  height: 400
  title: "Hello APP"

  Text {
    anchors.centerIn: parent
    text: "Hello world"
    font.pixelSize: 24
  }
}
