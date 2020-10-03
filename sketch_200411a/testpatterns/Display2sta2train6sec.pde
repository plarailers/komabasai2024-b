class Node {
    float x;
    float y;

    Node(float x, float y) {
        this.x = x;
        this.y = y;
    }

    void set(float x, float y) {
        this.x = x;
        this.y = y;
    }
}

class Display {
    int base = 0; // 初期時間
    int count; //スタートしてから経過した時間
    float tmp; //調整用
    int train = 30; //電車の大きさ
    Node node0 = new Node(100, 200);  // 本線
    Node node1 = new Node(300, 200);
    Node node2 = new Node(500, 200); 
    Node node3 = new Node(700, 200);
    Node node4 = new Node(900, 200);
    Node node5 = new Node(120, 300);  // 副本線
    Node node6 = new Node(280, 300);
    Node node7 = new Node(520, 300);
    Node node8 = new Node(680, 300);

    void setup() {
        PFont font = createFont("MS Gothic", 36);
        textFont(font);
    }
    void draw(State state){
        background(19,60,36);  // 背景色
        stroke(240,240,240);  // 線の色
        strokeWeight(5);  // 線の太さ
        line(node0.x, node0.y, node1.x, node1.y);  // 本線
        line(node1.x, node1.y, node2.x, node2.y);
        line(node2.x, node2.y, node3.x, node3.y);
        line(node3.x, node3.y, node4.x, node4.y);
        line(node5.x, node5.y, node6.x, node6.y);  // 副本線
        line(node7.x, node7.y, node8.x, node8.y);
        line(node0.x, node0.y, node5.x, node5.y);  // ナナメの線
        line(node1.x, node1.y, node6.x, node6.y);
        line(node2.x, node2.y, node7.x, node7.y);
        line(node3.x, node3.y, node8.x, node8.y);
        stroke(19,60,36);
        line(node0.x-10, node0.y-20, node0.x-10, node0.y+20);  // 区切り線
        line(node1.x+10, node0.y-20, node1.x+10, node0.y+20);
        line(node2.x-10, node0.y-20, node2.x-10, node0.y+20);
        line(node3.x+10, node0.y-20, node3.x+10, node0.y+20);
        line(node5.x+10, node0.y-20, node5.x+10, node5.y+20);  //  区切り線
        line(node6.x-10, node0.y-20, node6.x-10, node5.y+20);  //  区切り線
        line(node7.x+10, node0.y-20, node7.x+10, node5.y+20);  //  区切り線
        line(node8.x-10, node0.y-20, node8.x-10, node5.y+20);  //  区切り線
        // センサの描画
        fill(240);
        strokeWeight(0);
        rect(350-8, 200-8, 16, 16);
        // 文字類の描画
        textSize(20);
        textAlign(CENTER);
        fill(240);
        text("A 駅 (id=0)",200,50);
        text("B 駅 (id=1)",600,50);
        textSize(12);
        text("Section0",800,190);
        text("Section1",400,190);
        text("Section2 (1番線)",200,190);
        text("Section3 (2番線)",200,290);
        text("Section4 (1番線)",600,190);
        text("Section5 (2番線)",600,290);
        
        int ms = millis()/1000;
        // 以下で電車の座標を決定
        for (Train state_train : state.trainList) {
            int section_id = state_train.currentSection.id;
            int len = state_train.currentSection.length;
            float position_x = 100;
            float position_y = 200;
            switch (section_id) {  // x座標決定
                case 0:
                    position_x = 710 + 180 * state_train.getPosition();  break;
                case 1:
                    position_x = 310 + 180 * state_train.getPosition();  break;
                case 2:
                case 3:
                    position_x = 130 + 140 * state_train.getPosition();  break;
                case 4:
                case 5:
                    position_x = 530 + 140 * state_train.getPosition();  break;
            }
            switch (section_id) {  // y座標決定
                case 0:
                case 1:
                case 2:
                case 4:
                    position_y = 200;  break;
                case 3:
                case 5:
                    position_y = 300;  break;
            }
            // 電車の描画
            fill(255,0,0);  // 塗りつぶし色
            strokeWeight(0);
            stroke(19,60,36);
            triangle(position_x-15, position_y-15, position_x-15, position_y+15, position_x+15, position_y);
            fill(255);
            textSize(14);
            textAlign(LEFT);
            text(state_train.id ,position_x-10, position_y+7);  // trainId
            Info info = timetable.getByTrainId(state_train.id);
            String type;
            textSize(10);
            if (info != null) { 
                if (info.isArrival()) {
                    type = "着";
                } else if (info.isDeparture()) {
                    type = "発";
                } else {
                    type = "通";
                }
                text("次時刻:\n" + Station.getById(info.stationId).name + "駅 " +info.trackId+ "番線 " +info.time+type, position_x-10, position_y+20);
            }
        }

        // 時刻の描画
        fill(240);
        textSize(20);
        count = base + ms;
        text("time : "+count, 800, 400);


        // 信号描画
        Signal sig2Dep = Signal.R;  // Section2出発
        if (detectTrain(state.sectionList.get(1)) == null && state.junctionList.get(1).getInSection().id == 2) {
            sig2Dep = Signal.G;
        }
        drawSignal(300,170,2,sig2Dep);

        Signal sig3Dep = Signal.R;  // section3出発
        if (detectTrain(state.sectionList.get(1)) == null && state.junctionList.get(1).getInSection().id == 3) {
            sig3Dep = Signal.G;
        }
        drawSignal(300,330,2,sig3Dep);

        Signal sig2Arr = Signal.R;  // section2場内
        if (detectTrain(state.sectionList.get(2)) == null && state.junctionList.get(0).getPointedSection().id == 2) {
            sig2Arr = Signal.G;
        }
        drawSignal(110,140,2,sig2Arr);

        Signal sig3Arr = Signal.R;  // section3場内
        if (detectTrain(state.sectionList.get(3)) == null && state.junctionList.get(0).getPointedSection().id == 3) {
            sig3Arr = Signal.G;
        }
        drawSignal(100,170,2,sig3Arr);

        Signal sig4Dep = Signal.R;  // Section4出発
        if (detectTrain(state.sectionList.get(0)) == null && state.junctionList.get(3).getInSection().id == 4) {
            sig4Dep = Signal.G;
        }
        drawSignal(700,170,2,sig4Dep);

        Signal sig5Dep = Signal.R;  // section5出発
        if (detectTrain(state.sectionList.get(0)) == null && state.junctionList.get(3).getInSection().id == 5) {
            sig5Dep = Signal.G;
        }
        drawSignal(700,330,2,sig5Dep);

        Signal sig4Arr = Signal.R;  // section4場内
        if (detectTrain(state.sectionList.get(4)) == null && state.junctionList.get(2).getPointedSection().id == 4) {
            sig4Arr = Signal.G;
        }
        drawSignal(510,140,2,sig4Arr);

        Signal sig5Arr = Signal.R;  // section5場内
        if (detectTrain(state.sectionList.get(5)) == null && state.junctionList.get(2).getPointedSection().id == 5) {
            sig5Arr = Signal.G;
        }
        drawSignal(500,170,2,sig5Arr);
    }

    void drawSignal(float x, float y, int sigNum, Signal sig) {
        if (sigNum == 2) {  // 2灯式
            fill(19,60,36);
            stroke(240);
            strokeWeight(1);
            line(x, y, x+20, y);
            line(x, y-8, x, y+8);
            circle(x+22, y, 20);
            circle(x+38, y, 20);
            stroke(19,60,36);
            strokeWeight(2);
            rect(x+22, y-10, 16, 20);
            stroke(240);
            strokeWeight(1);
            line(x+22, y-10, x+38, y-10);
            line(x+22, y+10, x+38, y+10);
            stroke(19,60,36);
            strokeWeight(0);
            if (sig == Signal.R) {
                fill(255,0,0);
                circle(x+24, y, 10);
                fill(10);
                circle(x+36, y, 10);
            } else {
                fill(0,180,70);
                circle(x+36, y, 10);
                fill(10);
                circle(x+24, y, 10);
            }
        }

    }
}

enum Signal {
    R,
    Y,
    G
}
