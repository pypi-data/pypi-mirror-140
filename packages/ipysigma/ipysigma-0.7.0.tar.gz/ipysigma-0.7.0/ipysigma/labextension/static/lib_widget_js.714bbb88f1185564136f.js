(self["webpackChunkipysigma"] = self["webpackChunkipysigma"] || []).push([["lib_widget_js"],{

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) Yomguithereal
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;
//# sourceMappingURL=version.js.map

/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.SigmaView = exports.SigmaModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const graphology_1 = __importDefault(__webpack_require__(/*! graphology */ "webpack/sharing/consume/default/graphology/graphology"));
const worker_1 = __importDefault(__webpack_require__(/*! graphology-layout-forceatlas2/worker */ "./node_modules/graphology-layout-forceatlas2/worker.js"));
const graphology_layout_forceatlas2_1 = __importDefault(__webpack_require__(/*! graphology-layout-forceatlas2 */ "webpack/sharing/consume/default/graphology-layout-forceatlas2/graphology-layout-forceatlas2"));
const sigma_1 = __importDefault(__webpack_require__(/*! sigma */ "webpack/sharing/consume/default/sigma/sigma"));
const seedrandom_1 = __importDefault(__webpack_require__(/*! seedrandom */ "webpack/sharing/consume/default/seedrandom/seedrandom"));
const comma_number_1 = __importDefault(__webpack_require__(/*! comma-number */ "webpack/sharing/consume/default/comma-number/comma-number"));
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
// Import the CSS
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
/**
 * Model declaration.
 */
class SigmaModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: SigmaModel.model_name, _model_module: SigmaModel.model_module, _model_module_version: SigmaModel.model_module_version, _view_name: SigmaModel.view_name, _view_module: SigmaModel.view_module, _view_module_version: SigmaModel.view_module_version, data: { nodes: [], edges: [] }, height: 500, start_layout: false });
    }
}
exports.SigmaModel = SigmaModel;
SigmaModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
SigmaModel.model_name = 'SigmaModel';
SigmaModel.model_module = version_1.MODULE_NAME;
SigmaModel.model_module_version = version_1.MODULE_VERSION;
SigmaModel.view_name = 'SigmaView'; // Set to null if no view
SigmaModel.view_module = version_1.MODULE_NAME; // Set to null if no view
SigmaModel.view_module_version = version_1.MODULE_VERSION;
/**
 * Helper functions.
 */
function isValidNumber(value) {
    return typeof value === 'number' && !isNaN(value);
}
function buildGraph(data, rng) {
    const graph = graphology_1.default.from(data);
    graph.updateEachNodeAttributes((key, attr) => {
        // Random position for nodes without positions
        if (!isValidNumber(attr.x))
            attr.x = rng();
        if (!isValidNumber(attr.y))
            attr.y = rng();
        // If we don't have a label we keep the key instead
        if (!attr.label)
            attr.label = key;
        return attr;
    });
    return graph;
}
function selectSigmaSettings(graph) {
    const settings = {};
    console.log(graph);
    if (graph.type !== 'undirected') {
        settings.defaultEdgeType = 'arrow';
    }
    return settings;
}
function adjustDimensions(el, height) {
    el.style.height = height + 'px';
    el.style.width = '100%';
}
function createElement(tag, options) {
    const element = document.createElement(tag);
    const { className, style, innerHTML, title } = options || {};
    if (className)
        element.setAttribute('class', className);
    for (const prop in style) {
        element.style[prop] = style[prop];
    }
    if (innerHTML)
        element.innerHTML = innerHTML;
    if (title)
        element.setAttribute('title', title);
    return element;
}
const SPINNER_STATES = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
function createSpinner() {
    const span = createElement('span', { innerHTML: SPINNER_STATES[0] });
    let state = -1;
    let frame = null;
    const update = () => {
        state++;
        state %= SPINNER_STATES.length;
        span.innerHTML = SPINNER_STATES[state];
        frame = setTimeout(update, 80);
    };
    update();
    return [span, () => frame !== null && clearTimeout(frame)];
}
function createGraphDescription(graph) {
    let innerHTML = graph.multi ? 'Multi ' : '';
    innerHTML += graph.type === 'undirected' ? 'Undirected' : 'Directed';
    innerHTML += ` Graph<br><b>${comma_number_1.default(graph.order)}</b> nodes<br><b>${comma_number_1.default(graph.size)}</b> edges`;
    return createElement('div', {
        className: 'ipysigma-graph-description',
        innerHTML,
    });
}
/**
 * View declaration.
 */
class SigmaView extends base_1.DOMWidgetView {
    constructor() {
        super(...arguments);
        this.spinner = null;
    }
    render() {
        super.render();
        this.rng = seedrandom_1.default('ipysigma');
        this.el.classList.add('ipysigma-widget');
        const height = this.model.get('height');
        const data = this.model.get('data');
        const graph = buildGraph(data, this.rng);
        this.layout = new worker_1.default(graph, {
            settings: graphology_layout_forceatlas2_1.default.inferSettings(graph),
        });
        adjustDimensions(this.el, height);
        const container = document.createElement('div');
        this.el.appendChild(container);
        adjustDimensions(container, height);
        // Description
        this.el.appendChild(createGraphDescription(graph));
        // Camera controls
        this.zoomButton = createElement('div', {
            className: 'ipysigma-button ipysigma-zoom-button',
            innerHTML: 'zoom',
        });
        this.unzoomButton = createElement('div', {
            className: 'ipysigma-button ipysigma-unzoom-button',
            innerHTML: 'unzoom',
        });
        this.rescaleButton = createElement('div', {
            className: 'ipysigma-button ipysigma-rescale-button',
            innerHTML: 'rescale',
        });
        this.el.appendChild(this.zoomButton);
        this.el.appendChild(this.unzoomButton);
        this.el.appendChild(this.rescaleButton);
        // Layout controls
        this.layoutButton = createElement('div', {
            className: 'ipysigma-button ipysigma-layout-button',
            innerHTML: 'start layout',
        });
        this.el.appendChild(this.layoutButton);
        // Waiting for widget to be mounted to register events
        this.displayed.then(() => {
            this.renderer = new sigma_1.default(graph, container, selectSigmaSettings(graph));
            this.bindCameraHandlers();
            this.bindLayoutHandlers();
        });
    }
    bindCameraHandlers() {
        this.zoomButton.onclick = () => {
            this.renderer.getCamera().animatedZoom();
        };
        this.unzoomButton.onclick = () => {
            this.renderer.getCamera().animatedUnzoom();
        };
        this.rescaleButton.onclick = () => {
            this.renderer.getCamera().animatedReset();
        };
    }
    bindLayoutHandlers() {
        const stopLayout = () => {
            if (this.spinner) {
                this.spinner[1]();
                this.spinner = null;
            }
            this.layoutButton.innerHTML = 'start layout';
            this.layout.stop();
        };
        const startLayout = () => {
            this.spinner = createSpinner();
            this.layoutButton.innerHTML = 'stop layout - ';
            this.layoutButton.appendChild(this.spinner[0]);
            this.layout.start();
        };
        if (this.model.get('start_layout'))
            startLayout();
        this.layoutButton.onclick = () => {
            if (this.layout.isRunning()) {
                stopLayout();
            }
            else {
                startLayout();
            }
        };
    }
    remove() {
        // Cleanup to avoid leaks and free GPU slots
        if (this.renderer)
            this.renderer.kill();
        super.remove();
    }
}
exports.SigmaView = SigmaView;
//# sourceMappingURL=widget.js.map

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./css/widget.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/widget.css ***!
  \**************************************************************/
/***/ ((module, exports, __webpack_require__) => {

// Imports
var ___CSS_LOADER_API_IMPORT___ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
exports = ___CSS_LOADER_API_IMPORT___(false);
// Module
exports.push([module.id, ".ipysigma-widget {\n  margin: 0 10px;\n  padding: 0;\n  border: 1px solid #e0e0e0;\n}\n\n.ipysigma-widget .ipysigma-graph-description {\n  position: absolute;\n  top: 10px;\n  left: 10px;\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  padding: 5px 10px;\n  font-size: 0.8em;\n  font-style: italic;\n  z-index: 10;\n}\n\n.ipysigma-widget .ipysigma-button {\n  cursor: pointer;\n  position: absolute;\n  left: 10px;\n  text-align: center;\n  padding: 5px;\n  font-size: 0.8em;\n  z-index: 10;\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  user-select: none;\n}\n\n.ipysigma-widget .ipysigma-zoom-button {\n  top: 80px;\n}\n\n.ipysigma-widget .ipysigma-unzoom-button {\n  top: 114px;\n}\n\n.ipysigma-widget .ipysigma-rescale-button {\n  top: 148px;\n}\n\n.ipysigma-widget .ipysigma-layout-button {\n  top: 194px;\n}\n", ""]);
// Exports
module.exports = exports;


/***/ }),

/***/ "./css/widget.css":
/*!************************!*\
  !*** ./css/widget.css ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./widget.css */ "./node_modules/css-loader/dist/cjs.js!./css/widget.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"ipysigma","version":"0.7.0","description":"A custom Jupyter widget library to display graphs using sigma.js.","keywords":["sigma","graph","jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/Yomguithereal/ipysigma","bugs":{"url":"https://github.com/Yomguithereal/ipysigma/issues"},"license":"MIT","author":{"name":"Yomguithereal","email":"guillaume.plique@sciencespo.fr"},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/Yomguithereal/ipysigma"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ipysigma/labextension","clean:nbextension":"rimraf ipysigma/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","comma-number":"^2.1.0","graphology":"^0.24.1","graphology-layout-forceatlas2":"^0.8.2","seedrandom":"^3.0.5","sigma":"^2.2.0"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/comma-number":"^2.1.0","@types/jest":"^26.0.0","@types/seedrandom":"^3.0.2","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","csstype":"^3.0.10","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.0.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ipysigma/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js.714bbb88f1185564136f.js.map