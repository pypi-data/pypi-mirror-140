(self["webpackChunkipysigma"] = self["webpackChunkipysigma"] || []).push([["lib_widget_js"],{

/***/ "./lib/icons.js":
/*!**********************!*\
  !*** ./lib/icons.js ***!
  \**********************/
/***/ ((__unused_webpack_module, exports) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.fullscreenExitIcon = exports.fullscreenEnterIcon = exports.pauseIcon = exports.playIcon = exports.resetLayoutIcon = exports.resetZoomIcon = exports.unzoomIcon = exports.zoomIcon = void 0;
exports.zoomIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path><path d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z"></path></svg>`;
exports.unzoomIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zM7 9h5v1H7z"></path></svg>`;
exports.resetZoomIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M5 15H3v4c0 1.1.9 2 2 2h4v-2H5v-4zM5 5h4V3H5c-1.1 0-2 .9-2 2v4h2V5zm14-2h-4v2h4v4h2V5c0-1.1-.9-2-2-2zm0 16h-4v2h4c1.1 0 2-.9 2-2v-4h-2v4zM12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 6c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"></path></svg>`;
exports.resetLayoutIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M7.11 8.53 5.7 7.11C4.8 8.27 4.24 9.61 4.07 11h2.02c.14-.87.49-1.72 1.02-2.47zM6.09 13H4.07c.17 1.39.72 2.73 1.62 3.89l1.41-1.42c-.52-.75-.87-1.59-1.01-2.47zm1.01 5.32c1.16.9 2.51 1.44 3.9 1.61V17.9c-.87-.15-1.71-.49-2.46-1.03L7.1 18.32zM13 4.07V1L8.45 5.55 13 10V6.09c2.84.48 5 2.94 5 5.91s-2.16 5.43-5 5.91v2.02c3.95-.49 7-3.85 7-7.93s-3.05-7.44-7-7.93z"></path></svg>`;
exports.playIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg>`;
exports.pauseIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path></svg>`;
exports.fullscreenEnterIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"></path></svg>`;
exports.fullscreenExitIcon = `<svg width="20" height="20" focusable="false" viewBox="0 0 24 24"><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"></path></svg>`;
//# sourceMappingURL=icons.js.map

/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.generatePalette = exports.saveAsSVG = exports.saveAsGEXF = exports.saveAsJSON = exports.saveAsPNG = exports.renderAsDataURL = void 0;
// Taken and adapted from: https://github.com/jacomyal/sigma.js/blob/main/examples/png-snapshot/saveAsPNG.ts
const sigma_1 = __importDefault(__webpack_require__(/*! sigma */ "webpack/sharing/consume/default/sigma/sigma"));
const file_saver_1 = __importDefault(__webpack_require__(/*! file-saver */ "webpack/sharing/consume/default/file-saver/file-saver"));
const iwanthue_1 = __importDefault(__webpack_require__(/*! iwanthue */ "webpack/sharing/consume/default/iwanthue/iwanthue"));
const gexf = __importStar(__webpack_require__(/*! graphology-gexf/browser */ "./node_modules/graphology-gexf/browser/index.js"));
// @ts-ignore
const renderer_1 = __importDefault(__webpack_require__(/*! graphology-svg/renderer */ "./node_modules/graphology-svg/renderer.js"));
// @ts-ignore
const defaults_1 = __webpack_require__(/*! graphology-svg/defaults */ "./node_modules/graphology-svg/defaults.js");
function renderToAuxiliaryCanvas(renderer, inputLayers) {
    const { width, height } = renderer.getDimensions();
    // This pixel ratio is here to deal with retina displays.
    // Indeed, for dimensions W and H, on a retina display, the canvases
    // dimensions actually are 2 * W and 2 * H. Sigma properly deals with it, but
    // we need to readapt here:
    const pixelRatio = window.devicePixelRatio || 1;
    const tmpRoot = document.createElement('DIV');
    tmpRoot.style.width = `${width}px`;
    tmpRoot.style.height = `${height}px`;
    tmpRoot.style.position = 'absolute';
    tmpRoot.style.right = '101%';
    tmpRoot.style.bottom = '101%';
    document.body.appendChild(tmpRoot);
    // Instantiate sigma:
    const tmpRenderer = new sigma_1.default(renderer.getGraph(), tmpRoot, renderer.getSettings());
    // Copy camera and force to render now, to avoid having to wait the schedule /
    // debounce frame:
    tmpRenderer.getCamera().setState(renderer.getCamera().getState());
    tmpRenderer.refresh();
    // Create a new canvas, on which the different layers will be drawn:
    const canvas = document.createElement('CANVAS');
    canvas.setAttribute('width', width * pixelRatio + '');
    canvas.setAttribute('height', height * pixelRatio + '');
    const ctx = canvas.getContext('2d');
    // Draw a white background first:
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, width * pixelRatio, height * pixelRatio);
    // For each layer, draw it on our canvas:
    const canvases = tmpRenderer.getCanvases();
    const layers = inputLayers
        ? inputLayers.filter((id) => !!canvases[id])
        : Object.keys(canvases);
    layers.forEach((id) => {
        ctx.drawImage(canvases[id], 0, 0, width * pixelRatio, height * pixelRatio, 0, 0, width * pixelRatio, height * pixelRatio);
    });
    return [
        canvas,
        () => {
            // Cleanup:
            tmpRenderer.kill();
            tmpRoot.remove();
        },
    ];
}
function renderAsDataURL(renderer) {
    const [canvas, cleanup] = renderToAuxiliaryCanvas(renderer);
    const dataURL = canvas.toDataURL();
    cleanup();
    return dataURL;
}
exports.renderAsDataURL = renderAsDataURL;
function saveAsPNG(renderer) {
    const [canvas, cleanup] = renderToAuxiliaryCanvas(renderer);
    // Save the canvas as a PNG image:
    canvas.toBlob((blob) => {
        if (blob)
            file_saver_1.default.saveAs(blob, 'graph.png');
        cleanup();
    }, 'image/png');
}
exports.saveAsPNG = saveAsPNG;
function saveAsJSON(renderer) {
    const data = JSON.stringify(renderer.getGraph(), null, 2);
    file_saver_1.default.saveAs(new Blob([data], { type: 'application/json' }), 'graph.json');
}
exports.saveAsJSON = saveAsJSON;
function saveAsGEXF(renderer) {
    const data = gexf.write(renderer.getGraph());
    file_saver_1.default.saveAs(new Blob([data], { type: 'application/xml' }), 'graph.gexf');
}
exports.saveAsGEXF = saveAsGEXF;
function saveAsSVG(renderer) {
    const data = renderer_1.default(renderer.getGraph(), defaults_1.DEFAULTS);
    file_saver_1.default.saveAs(new Blob([data], { type: 'image/svg+xml' }), 'graph.svg');
}
exports.saveAsSVG = saveAsSVG;
const DEFAULT_COLOR_SPACE = {
    cmin: 25.59,
    cmax: 55.59,
    lmin: 60.94,
    lmax: 90.94,
};
const SINGLE_COLOR_PALETTE = ['#999'];
function generatePalette(name, count) {
    if (count === 1)
        return SINGLE_COLOR_PALETTE;
    return iwanthue_1.default(count, {
        colorSpace: DEFAULT_COLOR_SPACE,
        seed: name,
        clustering: 'force-vector',
        attempts: 5,
    });
}
exports.generatePalette = generatePalette;
//# sourceMappingURL=utils.js.map

/***/ }),

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
const choices_js_1 = __importDefault(__webpack_require__(/*! choices.js */ "webpack/sharing/consume/default/choices.js/choices.js"));
const screenfull_1 = __importDefault(__webpack_require__(/*! screenfull */ "webpack/sharing/consume/default/screenfull/screenfull"));
const multi_set_1 = __importDefault(__webpack_require__(/*! mnemonist/multi-set */ "./node_modules/mnemonist/multi-set.js"));
const d3_scale_1 = __webpack_require__(/*! d3-scale */ "webpack/sharing/consume/default/d3-scale/d3-scale");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
const utils_1 = __webpack_require__(/*! ./utils */ "./lib/utils.js");
const icons_1 = __webpack_require__(/*! ./icons */ "./lib/icons.js");
__webpack_require__(/*! choices.js/public/assets/styles/choices.min.css */ "./node_modules/choices.js/public/assets/styles/choices.min.css");
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
/**
 * Constants.
 */
const CAMERA_OFFSET = 0.65;
const NODE_VIZ_ATTRIBUTES = new Set(['label', 'size', 'color', 'x', 'y']);
const EDGE_VIZ_ATTRIBUTES = new Set(['label', 'size', 'color']);
const CATEGORY_MAX_COUNT = 10;
const DEFAULT_CONSTANT_NODE_SIZE = 5;
const DEFAULT_CONSTANT_EDGE_SIZE = 0.5;
const PALETTE_OVERFLOW = Symbol();
/**
 * Template.
 */
const TEMPLATE = `
<div id="ipysigma-container"></div>
<div id="ipysigma-left-panel">
  <div id="ipysigma-graph-description"></div>
  <div>
    <button id="ipysigma-zoom-button" class="ipysigma-button ipysigma-svg-icon" title="zoom">
      ${icons_1.zoomIcon}
    </button>
    <button id="ipysigma-unzoom-button" class="ipysigma-button ipysigma-svg-icon" title="unzoom">
      ${icons_1.unzoomIcon}
    </button>
    <button id="ipysigma-reset-zoom-button" class="ipysigma-button ipysigma-svg-icon" title="reset zoom">
      ${icons_1.resetZoomIcon}
    </button>
  </div>
  <div>
    <button id="ipysigma-fullscreen-button" class="ipysigma-button ipysigma-svg-icon" title="enter fullscreen">
      ${icons_1.fullscreenEnterIcon}
    </button>
  </div>
  <div id="ipysigma-layout-controls">
    <button id="ipysigma-layout-button" class="ipysigma-button ipysigma-svg-icon" title="start layout">
      ${icons_1.playIcon}
    </button>
    <button id="ipysigma-reset-layout-button" class="ipysigma-button ipysigma-svg-icon" title="reset layout">
      ${icons_1.resetLayoutIcon}
    </button>
  </div>
</div>
<div id="ipysigma-right-panel">
  <select id="ipysigma-search">
    <option value="">Search a node...</option>
  </select>
  <div id="ipysigma-information-display">
    <div id="ipysigma-information-display-tabs">
      <em id="ipysigma-information-legend-button" class="ipysigma-tab-button">legend</em>
      &middot;
      <em id="ipysigma-information-info-button" class="ipysigma-tab-button">info</em>
    </div>
    <hr>
    <div id="ipysigma-legend"></div>
    <div id="ipysigma-information-contents"></div>
  </div>
  <div id="ipysigma-download-controls">
    <button id="ipysigma-download-png-button" class="ipysigma-button">
      png
    </button>
    <button id="ipysigma-download-svg-button" class="ipysigma-button">
      svg
    </button>
    <button id="ipysigma-download-gexf-button" class="ipysigma-button">
      gexf
    </button>
    <button id="ipysigma-download-json-button" class="ipysigma-button">
      json
    </button>
  </div>
</div>
`;
/**
 * Model declaration.
 */
class SigmaModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: SigmaModel.model_name, _model_module: SigmaModel.model_module, _model_module_version: SigmaModel.model_module_version, _view_name: SigmaModel.view_name, _view_module: SigmaModel.view_module, _view_module_version: SigmaModel.view_module_version, data: { nodes: [], edges: [] }, height: 500, start_layout: false, snapshot: null, layout: null, clickableEdges: false, visual_variables: {} });
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
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
function renderAttributeValue(value) {
    const safe = escapeHtml('' + value);
    let type = 'unknown';
    if (typeof value === 'number') {
        type = 'number';
    }
    else if (typeof value === 'string') {
        type = 'string';
    }
    else if (typeof value === 'boolean') {
        type = 'boolean';
    }
    return `<span class="ipysigma-${type}" title="${type}">${safe}</span>`;
}
function collectLayout(graph) {
    const mapping = {};
    graph.forEachNode((node, attr) => {
        mapping[node] = { x: attr.x, y: attr.y };
    });
    return mapping;
}
function buildGraph(data, rng) {
    const graph = graphology_1.default.from(data);
    // Rectifications
    graph.updateEachNodeAttributes((key, attr) => {
        // Random position for nodes without positions
        if (!isValidNumber(attr.x))
            attr.x = rng();
        if (!isValidNumber(attr.y))
            attr.y = rng();
        return attr;
    });
    return graph;
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
function hide(el) {
    el.style.display = 'none';
}
function show(el) {
    el.style.display = 'block';
}
const SPINNER_STATES = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
function createSpinner() {
    const span = createElement('span', {
        className: 'ipysigma-spinner',
        innerHTML: SPINNER_STATES[0],
    });
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
function getGraphDescription(graph) {
    let graphTitle = `${graph.multi ? 'Multi ' : ''}${graph.type === 'undirected' ? 'Undirected' : 'Directed'} Graph`;
    let html = `<u>${graphTitle}</u><br><b>${comma_number_1.default(graph.order)}</b> nodes<br><b>${comma_number_1.default(graph.size)}</b> edges`;
    return html;
}
/**
 * View declaration.
 */
class SigmaView extends base_1.DOMWidgetView {
    constructor() {
        super(...arguments);
        this.singleton = true;
        this.layoutSpinner = null;
        this.currentTab = 'legend';
        this.selectedNode = null;
        this.selectedEdge = null;
        this.focusedNodes = null;
    }
    renderSingletonError() {
        this.el.innerHTML =
            '<i>You cannot render two independent views of the same Sigma widget, sorry...</i>';
    }
    render() {
        super.render();
        // Lock management
        if (this.model.get('singleton_lock')) {
            this.renderSingletonError();
            this.singleton = false;
            return;
        }
        this.model.set('singleton_lock', true);
        this.touch();
        this.rng = seedrandom_1.default('ipysigma');
        this.el.classList.add('ipysigma-widget');
        const height = this.model.get('height');
        const data = this.model.get('data');
        const graph = buildGraph(data, this.rng);
        this.graph = graph;
        this.saveLayout();
        this.originalLayoutPositions = collectLayout(graph);
        this.layout = new worker_1.default(graph, {
            settings: graphology_layout_forceatlas2_1.default.inferSettings(graph),
        });
        this.el.insertAdjacentHTML('beforeend', TEMPLATE);
        this.el.style.width = '100%';
        this.el.style.height = height + 'px';
        this.container = this.el.querySelector('#ipysigma-container');
        this.container.style.width = '100%';
        this.container.style.height = height + 'px';
        // Description
        const description = this.el.querySelector('#ipysigma-graph-description');
        description.innerHTML = getGraphDescription(graph);
        // Camera controls
        this.zoomButton = this.el.querySelector('#ipysigma-zoom-button');
        this.unzoomButton = this.el.querySelector('#ipysigma-unzoom-button');
        this.resetZoomButton = this.el.querySelector('#ipysigma-reset-zoom-button');
        // Fullscreen controls
        this.fullscreenButton = this.el.querySelector('#ipysigma-fullscreen-button');
        // Layout controls
        this.layoutControls = this.el.querySelector('#ipysigma-layout-controls');
        this.layoutButton = this.el.querySelector('#ipysigma-layout-button');
        this.resetLayoutButton = this.el.querySelector('#ipysigma-reset-layout-button');
        // Search
        var searchContainer = this.el.querySelector('#ipysigma-search');
        const nodeLabelAttribute = this.model.get('visual_variables').node_label.attribute;
        const options = graph.mapNodes((key, attr) => {
            let labelParts = [escapeHtml(key)];
            const label = attr[nodeLabelAttribute];
            if (label && label !== key) {
                labelParts.push(` <small style="font-size: 75%;">${escapeHtml(label)}</small>`);
            }
            return { value: key, label: labelParts.join(' ') };
        });
        this.choices = new choices_js_1.default(searchContainer, {
            allowHTML: true,
            removeItemButton: true,
            renderChoiceLimit: 10,
            choices: options,
            itemSelectText: '',
            position: 'bottom',
        });
        this.infoElement = this.el.querySelector('#ipysigma-information-contents');
        this.legendElement = this.el.querySelector('#ipysigma-legend');
        this.nodeInfoButton = this.el.querySelector('#ipysigma-information-info-button');
        this.legendButton = this.el.querySelector('#ipysigma-information-legend-button');
        this.changeInformationDisplayTab('legend');
        // Download controls
        this.downloadPNGButton = this.el.querySelector('#ipysigma-download-png-button');
        this.downloadGEXFButton = this.el.querySelector('#ipysigma-download-gexf-button');
        this.downloadSVGButton = this.el.querySelector('#ipysigma-download-svg-button');
        this.downloadJSONButton = this.el.querySelector('#ipysigma-download-json-button');
        // Waiting for widget to be mounted to register events
        this.displayed.then(() => {
            var _a;
            const clickableEdges = this.model.get('clickable_edges');
            const rendererSettings = {
                zIndex: true,
                defaultEdgeType: graph.type !== 'undirected' ? 'arrow' : 'line',
                enableEdgeClickEvents: clickableEdges,
                enableEdgeHoverEvents: clickableEdges,
            };
            // Gathering info about the graph to build reducers correctly
            const visualVariables = this.model.get('visual_variables');
            // Nodes
            let nodeColorPalette = null;
            let nodeColorCategory = visualVariables.node_color.type === 'category'
                ? visualVariables.node_color.attribute
                : null;
            const nodeCategoryFrequencies = new multi_set_1.default();
            let nodeSizeAttribute = visualVariables.node_size.type === 'continuous'
                ? visualVariables.node_size.attribute
                : 'size';
            let minNodeSize = Infinity;
            let maxNodeSize = -Infinity;
            let nodeLabelAttribute = visualVariables.node_label.attribute;
            graph.forEachNode((node, attr) => {
                if (nodeColorCategory) {
                    nodeCategoryFrequencies.add(attr[nodeColorCategory]);
                }
                const size = attr[nodeSizeAttribute];
                if (typeof size === 'number') {
                    if (size < minNodeSize)
                        minNodeSize = size;
                    if (size > maxNodeSize)
                        maxNodeSize = size;
                }
            });
            if (nodeColorCategory) {
                const count = Math.min(nodeCategoryFrequencies.dimension, CATEGORY_MAX_COUNT);
                const colors = utils_1.generatePalette(nodeColorCategory, count);
                nodeColorPalette = {
                    [PALETTE_OVERFLOW]: count < nodeCategoryFrequencies.dimension,
                };
                nodeCategoryFrequencies.top(count).forEach(([value], i) => {
                    nodeColorPalette[value] = colors[i];
                });
            }
            const hasConstantNodeSizes = minNodeSize === Infinity || minNodeSize === maxNodeSize;
            rendererSettings.labelRenderedSizeThreshold = hasConstantNodeSizes
                ? DEFAULT_CONSTANT_NODE_SIZE
                : Math.min(maxNodeSize, 6);
            let nodeSizeScale = null;
            if (!hasConstantNodeSizes &&
                visualVariables.node_size.type === 'continuous') {
                nodeSizeScale = d3_scale_1.scaleLinear()
                    .domain([minNodeSize, maxNodeSize])
                    .range(visualVariables.node_size.range);
            }
            // Edges
            let edgeColorPalette = null;
            let edgeColorCategory = visualVariables.edge_color.type === 'category'
                ? visualVariables.edge_color.attribute
                : null;
            const edgeCategoryFrequencies = new multi_set_1.default();
            let edgeSizeAttribute = visualVariables.edge_size.type === 'continuous'
                ? visualVariables.edge_size.attribute
                : 'size';
            let minEdgeSize = Infinity;
            let maxEdgeSize = -Infinity;
            let edgeLabelAttribute = (_a = visualVariables.edge_label) === null || _a === void 0 ? void 0 : _a.attribute;
            if (edgeLabelAttribute) {
                rendererSettings.renderEdgeLabels = true;
            }
            graph.forEachEdge((edge, attr) => {
                if (edgeColorCategory) {
                    edgeCategoryFrequencies.add(attr[edgeColorCategory]);
                }
                const size = attr[edgeSizeAttribute];
                if (typeof size === 'number') {
                    if (size < minEdgeSize)
                        minEdgeSize = size;
                    if (size > maxEdgeSize)
                        maxEdgeSize = size;
                }
            });
            if (edgeColorCategory) {
                const count = Math.min(edgeCategoryFrequencies.dimension, CATEGORY_MAX_COUNT);
                const colors = utils_1.generatePalette(edgeColorCategory, count);
                edgeColorPalette = {
                    [PALETTE_OVERFLOW]: count < edgeCategoryFrequencies.dimension,
                };
                edgeCategoryFrequencies.top(count).forEach(([value], i) => {
                    edgeColorPalette[value] = colors[i];
                });
            }
            const hasConstantEdgeSizes = minEdgeSize === Infinity || minEdgeSize === maxEdgeSize;
            rendererSettings.labelRenderedSizeThreshold = hasConstantEdgeSizes
                ? DEFAULT_CONSTANT_EDGE_SIZE
                : Math.min(maxEdgeSize, 6);
            let edgeSizeScale = null;
            if (!hasConstantEdgeSizes &&
                visualVariables.edge_size.type === 'continuous') {
                edgeSizeScale = d3_scale_1.scaleLinear()
                    .domain([minEdgeSize, maxEdgeSize])
                    .range(visualVariables.edge_size.range);
            }
            this.updateLegend(visualVariables, {
                nodeColor: nodeColorPalette,
                edgeColor: edgeColorPalette,
            });
            // Node reducer
            rendererSettings.nodeReducer = (node, data) => {
                const displayData = Object.assign({}, data);
                // Visual variables
                if (nodeColorCategory && nodeColorPalette) {
                    displayData.color =
                        nodeColorPalette[data[nodeColorCategory]] || '#999';
                }
                if (hasConstantNodeSizes) {
                    displayData.size = DEFAULT_CONSTANT_NODE_SIZE;
                }
                else if (nodeSizeScale) {
                    displayData.size = nodeSizeScale(data[nodeSizeAttribute] || 1);
                }
                displayData.label = data[nodeLabelAttribute] || node;
                // Transient state
                if (node === this.selectedNode) {
                    displayData.highlighted = true;
                }
                if (this.focusedNodes && !this.focusedNodes.has(node)) {
                    displayData.color = 'lightgray';
                    displayData.zIndex = 0;
                    displayData.size = displayData.size ? displayData.size / 2 : 1;
                }
                else {
                    displayData.zIndex = 1;
                }
                return displayData;
            };
            // Edge reducer
            rendererSettings.edgeReducer = (edge, data) => {
                const displayData = Object.assign({}, data);
                // Visual variables
                if (edgeColorCategory && edgeColorPalette) {
                    displayData.color =
                        edgeColorPalette[data[edgeColorCategory]] || '#ccc';
                }
                if (hasConstantEdgeSizes) {
                    displayData.size = DEFAULT_CONSTANT_EDGE_SIZE;
                }
                else if (edgeSizeScale) {
                    displayData.size = edgeSizeScale(data[edgeSizeAttribute] || 1);
                }
                if (edgeLabelAttribute) {
                    displayData.label = data[edgeLabelAttribute] || edge;
                }
                // Transient state
                if (this.focusedNodes) {
                    const [source, target] = graph.extremities(edge);
                    if (source !== this.selectedNode && target !== this.selectedNode) {
                        displayData.hidden = true;
                    }
                }
                return displayData;
            };
            this.renderer = new sigma_1.default(graph, this.container, rendererSettings);
            this.renderer.getCamera().setState({ x: CAMERA_OFFSET });
            this.clearSelectedItem();
            this.bindMessageHandlers();
            this.bindRendererHandlers();
            this.bindChoicesHandlers();
            this.bindInformationDisplayHandlers();
            this.bindDownloadHandlers();
            this.bindCameraHandlers();
            this.bindFullscreenHandlers();
            this.bindLayoutHandlers();
        });
    }
    renderSnapshot() {
        this.model.set('snapshot', utils_1.renderAsDataURL(this.renderer));
        this.touch();
    }
    saveLayout() {
        const mapping = collectLayout(this.graph);
        this.model.set('layout', mapping);
        this.touch();
    }
    resetLayout() {
        this.model.set('layout', this.originalLayoutPositions);
        this.touch();
    }
    changeInformationDisplayTab(tab) {
        if (tab === 'legend') {
            hide(this.infoElement);
            show(this.legendElement);
            this.legendButton.classList.remove('selectable');
            this.nodeInfoButton.classList.add('selectable');
        }
        else {
            hide(this.legendElement);
            show(this.infoElement);
            this.legendButton.classList.add('selectable');
            this.nodeInfoButton.classList.remove('selectable');
        }
    }
    updateLegend(variables, palettes) {
        function renderLegend(title, variable, palette) {
            let html = `<b>${title}</b><br>`;
            const source = variable.attribute.startsWith('$$')
                ? 'kwarg'
                : 'attribute';
            const name = variable.attribute.startsWith('$$')
                ? variable.attribute.slice(2)
                : variable.attribute;
            if (variable.type === 'raw') {
                html += `<span class="ipysigma-keyword">${escapeHtml(name)}</span> ${source}`;
            }
            else if (variable.type === 'continuous') {
                html += `<span class="ipysigma-keyword">${escapeHtml(name)}</span> ${source} (scaled to <span class="ipysigma-number">${variable.range[0]}</span>-<span class="ipysigma-number">${variable.range[1]}</span> px)`;
            }
            else if (variable.type === 'category') {
                html += `<span class="ipysigma-keyword">${escapeHtml(name)}</span> ${source} as a category:`;
                const paletteItems = [];
                if (palette) {
                    for (const k in palette) {
                        paletteItems.push(`<span style="color: ${palette[k]}">■</span> ${k}`);
                    }
                    if (palette[PALETTE_OVERFLOW]) {
                        paletteItems.push('<span style="color: #999">■</span> ...');
                    }
                }
                else {
                    paletteItems.push('<span style="color: #999">■</span> default');
                }
                html += '<br>' + paletteItems.join('<br>');
            }
            return html;
        }
        const items = [
            renderLegend('Node labels', variables.node_label),
            renderLegend('Node colors', variables.node_color, palettes.nodeColor),
            renderLegend('Node sizes', variables.node_size),
            renderLegend('Edge colors', variables.edge_color, palettes.edgeColor),
            renderLegend('Edge sizes', variables.edge_size),
        ];
        if (variables.edge_label) {
            items.push(renderLegend('Edge labels', variables.edge_label));
        }
        this.legendElement.innerHTML = items.join('<hr>');
    }
    clearSelectedItem() {
        this.selectedEdge = null;
        this.selectedNode = null;
        this.focusedNodes = null;
        if (this.model.get('clickable_edges')) {
            this.infoElement.innerHTML =
                '<i>Click on a node/edge or search a node to display information about it...</i>';
        }
        else {
            this.infoElement.innerHTML =
                '<i>Click on a node or search a node to display information about it...</i>';
        }
        this.changeInformationDisplayTab('legend');
        this.renderer.refresh();
    }
    selectItem(type, key) {
        const graph = this.graph;
        if (type === 'node') {
            this.selectedEdge = null;
            this.selectedNode = key;
            const focusedNodes = new Set();
            focusedNodes.add(this.selectedNode);
            graph.forEachNeighbor(key, (neighbor) => {
                focusedNodes.add(neighbor);
            });
            this.focusedNodes = focusedNodes;
        }
        else {
            this.selectedEdge = key;
            this.selectedNode = null;
            this.focusedNodes = null;
        }
        const attr = type === 'node'
            ? graph.getNodeAttributes(key)
            : graph.getEdgeAttributes(key);
        let innerHTML = `<b>Node</b> <i>${escapeHtml(key)}</i>`;
        const kwargInfo = [];
        const vizInfo = [];
        const info = [];
        const vizAttributes = type === 'node' ? NODE_VIZ_ATTRIBUTES : EDGE_VIZ_ATTRIBUTES;
        for (let k in attr) {
            let target = info;
            if (vizAttributes.has(k))
                target = vizInfo;
            else if (k.startsWith('$$'))
                target = kwargInfo;
            target.push(`<b>${k.startsWith('$$') ? k.slice(2) : k}</b> ${renderAttributeValue(attr[k])}`);
        }
        if (kwargInfo.length !== 0)
            innerHTML += '<hr>From kwargs:<br>' + kwargInfo.join('<br>');
        if (info.length !== 0)
            innerHTML += `<hr>Attributes:<br>` + info.join('<br>');
        if (vizInfo.length !== 0)
            innerHTML += '<hr>Known viz data:<br>' + vizInfo.join('<br>');
        if (type === 'node') {
            innerHTML += '<hr>Computed metrics:<br>';
            innerHTML += `<b>degree</b> ${renderAttributeValue(graph.degree(key))}<br>`;
            if (graph.directedSize !== 0) {
                innerHTML += `<b>indegree</b> ${renderAttributeValue(graph.inDegree(key))}<br>`;
                innerHTML += `<b>outdegree</b> ${renderAttributeValue(graph.outDegree(key))}<br>`;
            }
        }
        this.infoElement.innerHTML = innerHTML;
        this.changeInformationDisplayTab('info');
        this.renderer.refresh();
    }
    bindMessageHandlers() {
        this.model.on('msg:custom', (content) => {
            if (content.msg === 'render_snapshot') {
                this.renderSnapshot();
            }
        });
    }
    bindRendererHandlers() {
        this.renderer.on('enterNode', () => {
            this.container.style.cursor = 'pointer';
        });
        this.renderer.on('leaveNode', () => {
            this.container.style.cursor = 'default';
        });
        this.renderer.on('clickNode', ({ node }) => {
            if (node === this.selectedNode)
                return;
            this.selectItem('node', node);
            this.choices.setChoiceByValue(node);
        });
        this.renderer.on('clickStage', () => {
            if (!this.selectedNode)
                return;
            this.clearSelectedItem();
            this.choices.setChoiceByValue('');
        });
        if (this.model.get('clickable_edges')) {
            this.renderer.on('enterEdge', () => {
                this.container.style.cursor = 'pointer';
            });
            this.renderer.on('leaveEdge', () => {
                this.container.style.cursor = 'default';
            });
            this.renderer.on('clickEdge', ({ edge }) => {
                if (edge === this.selectedEdge)
                    return;
                this.selectItem('edge', edge);
            });
        }
    }
    bindChoicesHandlers() {
        this.choices.passedElement.element.addEventListener('change', (event) => {
            const node = event.detail.value;
            if (node === this.selectedNode)
                return;
            if (!node)
                return this.clearSelectedItem();
            this.selectItem('node', node);
        });
    }
    bindInformationDisplayHandlers() {
        this.legendButton.onclick = () => {
            if (!this.legendButton.classList.contains('selectable'))
                return;
            this.changeInformationDisplayTab('legend');
        };
        this.nodeInfoButton.onclick = () => {
            if (!this.nodeInfoButton.classList.contains('selectable'))
                return;
            this.changeInformationDisplayTab('info');
        };
    }
    bindDownloadHandlers() {
        this.downloadPNGButton.onclick = () => {
            utils_1.saveAsPNG(this.renderer);
        };
        this.downloadGEXFButton.onclick = () => {
            utils_1.saveAsGEXF(this.renderer);
        };
        this.downloadSVGButton.onclick = () => {
            utils_1.saveAsSVG(this.renderer);
        };
        this.downloadJSONButton.onclick = () => {
            utils_1.saveAsJSON(this.renderer);
        };
    }
    bindCameraHandlers() {
        this.zoomButton.onclick = () => {
            this.renderer.getCamera().animatedZoom();
        };
        this.unzoomButton.onclick = () => {
            this.renderer.getCamera().animatedUnzoom();
        };
        this.resetZoomButton.onclick = () => {
            this.renderer
                .getCamera()
                .animate({ ratio: 1, x: CAMERA_OFFSET, y: 0.5, angle: 0 });
        };
    }
    bindFullscreenHandlers() {
        this.fullscreenButton.onclick = () => {
            if (screenfull_1.default.isFullscreen) {
                screenfull_1.default.exit();
                this.container.style.height = this.model.get('height') + 'px';
                this.fullscreenButton.innerHTML = icons_1.fullscreenEnterIcon;
                this.fullscreenButton.setAttribute('title', 'enter fullscreen');
            }
            else {
                screenfull_1.default.request(this.el);
                this.container.style.height = '100%';
                this.fullscreenButton.innerHTML = icons_1.fullscreenExitIcon;
                this.fullscreenButton.setAttribute('title', 'exit fullscreen');
            }
        };
    }
    bindLayoutHandlers() {
        hide(this.resetLayoutButton);
        const stopLayout = () => {
            if (this.layoutSpinner) {
                this.layoutControls.removeChild(this.layoutSpinner[0]);
                this.layoutSpinner[1]();
                this.layoutSpinner = null;
            }
            this.layoutButton.innerHTML = icons_1.playIcon;
            this.layoutButton.setAttribute('title', 'start layout');
            this.layout.stop();
            this.saveLayout();
            show(this.resetLayoutButton);
        };
        const startLayout = () => {
            this.layoutSpinner = createSpinner();
            this.layoutButton.innerHTML = icons_1.pauseIcon;
            this.layoutControls.appendChild(this.layoutSpinner[0]);
            this.layoutButton.setAttribute('title', 'stop layout');
            this.layout.start();
            hide(this.resetLayoutButton);
        };
        const resetLayout = () => {
            hide(this.resetLayoutButton);
            this.resetLayout();
            this.graph.updateEachNodeAttributes((node, attr) => {
                const pos = this.originalLayoutPositions[node];
                attr.x = pos.x;
                attr.y = pos.y;
                return attr;
            });
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
        this.resetLayoutButton.onclick = () => {
            resetLayout();
        };
    }
    remove() {
        // Cleanup to avoid leaks and free GPU slots
        if (this.renderer)
            this.renderer.kill();
        if (this.singleton) {
            this.model.set('singleton_lock', false);
            this.touch();
        }
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
exports.push([module.id, "/* Choices.js overrides */\n.choices {\n  margin-bottom: 5px;\n}\n\n.choices__inner {\n  border-radius: 0;\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  box-sizing: border-box;\n}\n\n.choices__item--selectable {\n  padding-right: 0px !important;\n}\n\n/* Ipysigma own styles */\n.ipysigma-widget {\n  background-color: white;\n  margin: 0;\n  padding: 0;\n  border: 1px solid #e0e0e0;\n  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;\n}\n\n.ipysigma-widget hr {\n  height: 1px;\n  border: none;\n  background-color: #e0e0e0;\n  margin-top: 6px;\n  margin-bottom: 6px;\n}\n\n.ipysigma-widget #ipysigma-left-panel {\n  position: absolute;\n  top: 10px;\n  left: 10px;\n}\n\n.ipysigma-widget #ipysigma-right-panel {\n  position: absolute;\n  top: 10px;\n  right: 10px;\n  width: 250px;\n  height: calc(100% - 20px);\n}\n\n.ipysigma-widget #ipysigma-graph-description {\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  padding: 5px 10px;\n  font-size: 12px;\n  font-style: italic;\n  line-height: 16px;\n}\n\n.ipysigma-widget .ipysigma-button {\n  cursor: pointer;\n  text-align: center;\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  user-select: none;\n}\n\n.ipysigma-widget .ipysigma-button:hover {\n  border-color: grey;\n}\n\n.ipysigma-widget .ipysigma-svg-icon {\n  width: 32px;\n  height: 32px;\n  font-size: 24px;\n  line-height: 30px;\n  box-sizing: border-box;\n}\n\n.ipysigma-widget #ipysigma-zoom-button {\n  margin-top: 10px;\n}\n\n.ipysigma-widget #ipysigma-unzoom-button {\n  margin-top: 10px;\n}\n\n.ipysigma-widget #ipysigma-reset-zoom-button {\n  margin-top: 10px;\n}\n\n.ipysigma-widget #ipysigma-fullscreen-button {\n  margin-top: 10px;\n}\n\n.ipysigma-widget #ipysigma-layout-controls {\n  width: 100%;\n  margin-top: 10px;\n  display: flex;\n}\n\n.ipysigma-widget #ipysigma-reset-layout-button {\n  margin-left: 4px;\n}\n\n.ipysigma-widget .ipysigma-spinner {\n  font-size: 20px;\n  padding-left: 5px;\n  line-height: 26px;\n}\n\n.ipysigma-widget .ipysigma-tab-button.selectable {\n  color: cornflowerblue;\n  text-decoration: underline;\n  cursor: pointer;\n}\n\n.ipysigma-widget #ipysigma-information-display {\n  width: 100%;\n  height: calc(100% - 45px - 5px - 30px);\n  overflow-y: auto;\n  background-color: white;\n  border: 1px solid #e0e0e0;\n  box-sizing: border-box;\n  font-size: 12px;\n  font-style: italic;\n  line-height: 16px;\n  padding: 10px;\n}\n\n.ipysigma-widget #ipysigma-information-contents,\n.ipysigma-widget #ipysigma-legend {\n  font-family: monospace;\n}\n\n.ipysigma-widget .ipysigma-string {\n  color: #bc2828;\n}\n\n.ipysigma-widget .ipysigma-number {\n  color: #008800;\n}\n\n.ipysigma-widget .ipysigma-boolean,\n.ipysigma-widget .ipysigma-keyword {\n  color: #0457ab;\n}\n\n.ipysigma-widget #ipysigma-download-controls {\n  margin-top: 5px;\n  /* display: flex; */\n  height: 30px;\n}\n\n.ipysigma-widget #ipysigma-download-png-button,\n.ipysigma-widget #ipysigma-download-svg-button,\n.ipysigma-widget #ipysigma-download-gexf-button {\n  margin-right: 3px;\n}\n", ""]);
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
module.exports = JSON.parse('{"name":"ipysigma","version":"0.7.0","description":"A custom Jupyter widget library to display graphs using sigma.js.","keywords":["sigma","graph","jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/Yomguithereal/ipysigma","bugs":{"url":"https://github.com/Yomguithereal/ipysigma/issues"},"license":"MIT","author":{"name":"Yomguithereal","email":"guillaume.plique@sciencespo.fr"},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/Yomguithereal/ipysigma"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ipysigma/labextension","clean:nbextension":"rimraf ipysigma/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","choices.js":"^10.1.0","comma-number":"^2.1.0","d3-scale":"^4.0.2","file-saver":"^2.0.5","graphology":"^0.24.1","graphology-gexf":"^0.10.1","graphology-layout-forceatlas2":"^0.8.2","graphology-svg":"^0.1.3","iwanthue":"^1.5.1","mnemonist":"^0.39.0","screenfull":"^6.0.1","seedrandom":"^3.0.5","sigma":"^2.2.0"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/comma-number":"^2.1.0","@types/d3-scale":"^4.0.2","@types/file-saver":"^2.0.5","@types/jest":"^26.0.0","@types/seedrandom":"^3.0.2","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","csstype":"^3.0.10","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.0.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ipysigma/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js.4d60725d57f26215b8fd.js.map