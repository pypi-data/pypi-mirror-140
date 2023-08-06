class Instant {
  csrfToken = "";
  client;
  backendUri;
  websocketsUri;
  channels = new Set();
  handlers = {};
  verbose = false;
  _onMessage = (message) => console.log(JSON.stringify(message.data, null, "  "));
  set onMessage(func) {
    this._onMessage = func;
  }
  init(backendUri, websocketsUri, verbose = false) {
    this.backendUri = backendUri;
    this.websocketsUri = websocketsUri;
    this.verbose = verbose;
    this.client = new Centrifuge(`${this.websocketsUri}/connection/websocket`, {
      subscribeEndpoint: `${this.backendUri}/instant/subscribe/`,
      debug: verbose
    });
  }
  async connect(autosub = true) {
    if (autosub) {
      this.subscribeToAllChannels();
    }
    let end;
    const connected = new Promise(resolve => {
      end = resolve;
    });
    this.client.on("connect", function () {
      end(true);
    });
    this.client.connect();
    await connected;
  }
  subscribe(channel) {
    this.client.subscribe(channel.name, (message) => {
      const data = JSON.parse(message.data);
      if (channel.name in this.handlers) {
        this.handlers[channel.name](data)
      } else {
        this._onMessage(data);
      }
    });
  }
  unsubscribe(channel) {
    this.client.unsubscribe(channel.name, (context) => {
      console.log("Unsubscribe from", channel)
    });
  }
  subscribeToAllChannels() {
    this.channels.forEach((c) => {
      this.subscribe(c)
    });
  }
  addHandler(channel, func) {
    this.handlers[channel] = func;
  }
  removeHandler(channel) {
    delete this.handlers[channel];
  }
  async login(username, password) {
    //console.log("Login");
    const payload = {
      username: username,
      password: password
    };
    const opts = this._postHeader(payload);
    const uri = this.backendUri + "/instant/login/";
    const response = await fetch(uri, opts);
    if (!response.ok) {
      console.log("Response not ok", response);
      throw new Error(response.statusText);
    }
    const data = (await response.json());
    this._process_tokens(data);
  }
  async get_token() {
    const opts = this._postHeader({});
    const uri = this.backendUri + "/instant/get_token/";
    const response = await fetch(uri, opts);
    if (!response.ok) {
      console.log("Response not ok", response);
      throw new Error(response.statusText);
    }
    const data = (await response.json());
    this._process_tokens(data);
  }
  _postHeader(payload) {
    const header = {
      method: "post",
      credentials: "include",
      mode: "cors",
      body: JSON.stringify(payload)
    };
    header.headers = {
      "Content-Type": "application/json",
    };
    if (this.csrfToken !== "") {
      header.headers = {
        "Content-Type": "application/json",
        "X-CSRFToken": this.csrfToken
      };
    }
    return header;
  }
  _process_tokens(data) {
    if (this.verbose) {
      console.log("Tokens", JSON.stringify(data, null, "  "));
    }
    this.csrfToken = data.csrf_token;
    this.client.setToken(data.ws_token);
    data.channels.forEach((c) => {
      this.channels.add(c);
    });
  }
}

var $instant = new Instant();
