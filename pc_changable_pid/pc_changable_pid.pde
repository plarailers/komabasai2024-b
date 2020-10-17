import processing.serial.*;
import websockets.*;

Serial myPort;  // Create object from Serial class
WebsocketClient wsc;
double speed_id = 0.0;

String getTime() {
  return String.format("%02d:%02d:%02d", hour(), minute(), second());
}

void setup() {
  surface.setVisible(false);
  String osName = System.getProperty("os.name");
  boolean isMac = osName.startsWith("Mac");
  boolean isWindows = osName.startsWith("Windows");
  //Bluetoothのシリアルを選択
  if (isMac) {
    myPort = new Serial(this, "/dev/cu.ESP32-ESP32SPP", 115200);//Mac
    //myPort = new Serial(this, "/dev/cu.Bluetooth-Incoming-Port", 115200);//Macテスト用
  }
  if (isWindows) {
    // Bluetooth接続可能なデバイスを列挙
    ArrayList<BluetoothDevice> deviceList = discoverBluetoothDevicesForWindows();
    printArray(deviceList);
    for (BluetoothDevice device : deviceList) {
      if (device.name.equals("ESP32-Dr.")) {
        myPort = new Serial(this, device.port, 115200);
        break;
      }
    }
  }
  println(getTime(), "Bluetooth connected");
  wsc = new WebsocketClient(this, "wss://60jt3xl73m.execute-api.ap-northeast-1.amazonaws.com/dev");
  println(getTime(), "WebSocket connected");
}

void draw() {
  while (myPort.available() > 0) {  // 車輪が1回転した信号が来たら
    int data = myPort.read();
    println(getTime(), "[Bluetooth:read]", data);
    int input = pidCalc(speed_id);  // pid計算
    myPort.write(input);
  }
  stopCheck();
}

void webSocketEvent(String msg) {
  println(getTime(), "[WebSocketEvent]", msg);
  JSONObject json_msg = parseJSONObject(msg);
  if (!json_msg.isNull("speed")) {
    int tmp_speed = json_msg.getInt("speed");
    speed_id = speed_constrain(tmp_speed);
    println(getTime(), "[WebController:speed_id]", speed_id);
    if (speed == 0.0) {  // 止まっているときは動かしてあげる
      int input = INPUT_START;
      println("input=INPUT_START");
      myPort.write(input);
    }
  }
}

int speed_constrain(int tmp_speed) {
  if (tmp_speed > 0) {
    return (int)(SPEED_MIN + (SPEED_MAX - SPEED_MIN) * tmp_speed/255);
  } else {
    return 0;
  }
}
