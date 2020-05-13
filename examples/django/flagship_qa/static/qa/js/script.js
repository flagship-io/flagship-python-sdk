var app = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        envId: "",
        bucketing: true,
        visitorId: "test-visitor",
        context: "{\n}",
        envOk: false,
        envError: null,
        visitorOk: false,
        visitorError: null,
        eventOk: false,
        eventError: null,
        data: null,
        hit: {t: "EVENT"},
        hitTypes: ["EVENT", "TRANSACTION", "ITEM", "PAGE"],
        flagOk: false,
        flag: {name: "", type: "bool", defaultValue: "", activation: true},
        flagError: null,
        activate: {name: ""},
        activateOk: false,
        activateError: null
    },
    methods: {
        getEnv() {
            this.$http.get("/qa/currentEnv").then((response) => {
                // get body data
                this.currentEnv = response.body;
                this.bucketing = response.body.bucketing;
                this.envId = response.body.env_id;
            });
        },
        setEnv() {
            this.envOk = false;
            this.envError = null;
            this.$http
                .post("/qa/setEnv", {
                    environment_id: this.envId,
                    bucketing: this.bucketing,
                })
                .then(
                    (response) => {
                        // get body data
                        this.envOk = true;
                    },
                    (response) => {
                        this.envOk = false;
                        this.envError = response.body;
                    }
                );
        },
        setVisitor() {
            this.visitorOk = false;
            this.visitorError = null;
            this.data = null;

            this.$http
                .post("/qa/setVisitor", {
                    visitor_id: this.visitorId,
                    context: JSON.parse(this.context),
                })
                .then(
                    (response) => {
                        // get body data
                        this.data = response.body;
                        this.visitorOk = true;
                    },
                    (response) => {
                        this.visitorOk = false;
                        this.visitorError = response.body;
                    }
                );
        },
        sendHit() {
            this.eventOk = false;
            this.eventError = null;

            this.$http.post("/qa/sendHit", this.hit).then(
                () => {
                    this.eventOk = true;
                },
                (response) => {
                    this.eventOk = false;
                    this.eventError = response.body
                }
            );
        },
        getFlag() {
            this.flagOk = false;
            this.flagError = null;
            const {name, type, activation, defaultValue} = this.flag;

            if (!name || !type || !defaultValue) {
                this.flagOk = {err: "Missing flag name, type or default value"};
                this.flagError = null
                return;
            }

            this.$http
                .get(
                    `/qa/getFlag/${name}?type=${type}&activation=${activation}&defaultValue=${defaultValue}`
                )
                .then(
                    (response) => {
                        this.flagOk = response.body;
                        this.flagError = null
                    },
                    (response) => {
                        this.flagOk = false
                        this.flagError = response.body;
                    }
                );
        },
        send_activation() {
            this.activateOk = false;
            this.activateError = null

            const {name} = this.activate
            if (!name) {
                this.activateOk = {err: "Missing flag name, type or default value"};
                this.activateError = null
                return;
            }
            this.$http
                .get(
                    `/qa/activate/${name}`
                )
                .then(
                    (response) => {
                        this.activateOk = response.body;
                        this.activateError = null
                    },
                    (response) => {
                        this.activateOk = false
                        this.activateError = response.body;
                    }
                );
        }
    },
    mounted() {
        this.getEnv();
    },
});
