class Viewer {
  constructor() {
    this.peerId = this.randomId();
    this.peer = null;
    this.room = null;
    this.onauthenticate = function () { };
    this.onconnect = function () { };
    this.onstream = function () { };
    this.onexpire = function () { };
    this.ondata = function () { };
  }

  randomId() {
    var BASE62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    var length = 16;
    var id = '';
    for (var i = 0; i < length; i++) {
      id += BASE62[Math.floor(Math.random() * BASE62.length)];
    }
    return id;
  }

  authenticate(password) {
    var endpoint = new URL('https://script.google.com/macros/s/AKfycbwOHievy8jRNhB2SM2A0gL3V3Aku7cnklc28JUc2j-ixtxwXPI/exec');
    endpoint.searchParams.set('peerId', this.peerId);
    endpoint.searchParams.set('password', password);
    fetch(endpoint).then(function (res) { return res.json(); }).then(this.onauthenticate);
  }

  connect(credential) {
    this.peer = new Peer(this.peerId, {
      key: 'cd8035c6-1b5d-4f1b-a7db-ef6e7e811fac',
      credential: credential
    });
    this.peer.on('open', function () {
      this.room = this.peer.joinRoom('room', {
        mode: 'mesh'
      });
      this.room.on('open', function () {
        this.onconnect();
      }.bind(this));
      this.room.on('addstream', function (e) {
        this.onstream(e.stream);
      }.bind(this));
      this.room.on('data', function (e) {
        if (e.src === 'master') {
          this.ondata(e.data);
        }
      }.bind(this));
    }.bind(this));
    this.peer.on('expiresin', function (sec) {
      setTimeout(function () {
        this.onexpire();
      }.bind(this), sec * 1000);
    });
  }

  send(data) {
    if (this.room && this.room.open) {
      this.room.send(data);
    }
  }
}
