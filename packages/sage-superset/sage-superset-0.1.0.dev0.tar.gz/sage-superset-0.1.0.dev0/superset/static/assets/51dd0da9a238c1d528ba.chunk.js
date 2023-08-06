"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[2229],{332229:(module,__webpack_exports__,__webpack_require__)=>{__webpack_require__.r(__webpack_exports__),__webpack_require__.d(__webpack_exports__,{default:()=>__WEBPACK_DEFAULT_EXPORT__});var react__WEBPACK_IMPORTED_MODULE_0__=__webpack_require__(667294),_superset_ui_core__WEBPACK_IMPORTED_MODULE_1__=__webpack_require__(767190),_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__=__webpack_require__(455867),_superset_ui_core__WEBPACK_IMPORTED_MODULE_4__=__webpack_require__(208608),_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__=__webpack_require__(740962),_superset_ui_core__WEBPACK_IMPORTED_MODULE_7__=__webpack_require__(67869),_superset_ui_core__WEBPACK_IMPORTED_MODULE_8__=__webpack_require__(751995),_components_Echart__WEBPACK_IMPORTED_MODULE_5__=__webpack_require__(263475),_emotion_react__WEBPACK_IMPORTED_MODULE_2__=__webpack_require__(211965),enterModule;module=__webpack_require__.hmd(module),enterModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0,enterModule&&enterModule(module);var __signature__="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const defaultNumberFormatter=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_1__.JB)(),PROPORTION={KICKER:.1,HEADER:.3,SUBHEADER:.125,TRENDLINE:.3};class BigNumberVis extends react__WEBPACK_IMPORTED_MODULE_0__.PureComponent{getClassName(){const{className:e,showTrendLine:t,bigNumberFallback:r}=this.props,_=`superset-legacy-chart-big-number ${e} ${r?"is-fallback-value":""}`;return t?_:`${_} no-trendline`}createTemporaryContainer(){const e=document.createElement("div");return e.className=this.getClassName(),e.style.position="absolute",e.style.opacity="0",e}renderFallbackWarning(){const{bigNumberFallback:e,formatTime:t,showTimestamp:r}=this.props;return!e||r?null:(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("span",{className:"alert alert-warning",role:"alert",title:(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__.t)("Last available value seen on %s",t(e[0]))},(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__.t)("Not up to date"))}renderKicker(e){const{timestamp:t,showTimestamp:r,formatTime:_,width:a}=this.props;if(!r)return null;const n=null===t?"":_(t),i=this.createTemporaryContainer();document.body.append(i);const s=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_4__.Z)({text:n,maxWidth:a,maxHeight:e,className:"kicker",container:i});return i.remove(),(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:"kicker",style:{fontSize:s,height:e}},n)}renderHeader(e){const{bigNumber:t,headerFormatter:r,width:_}=this.props,a=null===t?(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__.t)("No data"):r(t),n=this.createTemporaryContainer();document.body.append(n);const i=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_4__.Z)({text:a,maxWidth:_,maxHeight:e,className:"header-line",container:n});return n.remove(),(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:"header-line",style:{fontSize:i,height:e}},a)}renderSubheader(e){const{bigNumber:t,subheader:r,width:_,bigNumberFallback:a}=this.props;let n=0;const i=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__.t)("No data after filtering or data is NULL for the latest time record"),s=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_3__.t)("Try applying different filters or ensuring your datasource has data");let o=r;if(null===t&&(o=a?s:i),o){const t=this.createTemporaryContainer();return document.body.append(t),n=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_4__.Z)({text:o,maxWidth:_,maxHeight:e,className:"subheader-line",container:t}),t.remove(),(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:"subheader-line",style:{fontSize:n,height:e}},o)}return null}renderTrendline(e){const{width:t,trendLineData:r,echartOptions:_}=this.props;return null!=r&&r.some((e=>null!==e[1]))?(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)(_components_Echart__WEBPACK_IMPORTED_MODULE_5__.Z,{width:Math.floor(t),height:e,echartOptions:_}):null}render(){const{showTrendLine:e,height:t,kickerFontSize:r,headerFontSize:_,subheaderFontSize:a}=this.props,n=this.getClassName();if(e){const e=Math.floor(PROPORTION.TRENDLINE*t),i=t-e;return(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:n},(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:"text-container",style:{height:i}},this.renderFallbackWarning(),this.renderKicker(Math.ceil(r*(1-PROPORTION.TRENDLINE)*t)),this.renderHeader(Math.ceil(_*(1-PROPORTION.TRENDLINE)*t)),this.renderSubheader(Math.ceil(a*(1-PROPORTION.TRENDLINE)*t))),this.renderTrendline(e))}return(0,_emotion_react__WEBPACK_IMPORTED_MODULE_2__.tZ)("div",{className:n,style:{height:t}},this.renderFallbackWarning(),this.renderKicker(r*t),this.renderHeader(Math.ceil(_*t)),this.renderSubheader(Math.ceil(a*t)))}__reactstandin__regenerateByEval(key,code){this[key]=eval(code)}}BigNumberVis.defaultProps={className:"",headerFormatter:defaultNumberFormatter,formatTime:_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__.Z,headerFontSize:PROPORTION.HEADER,kickerFontSize:PROPORTION.KICKER,mainColor:_superset_ui_core__WEBPACK_IMPORTED_MODULE_7__.E8,showTimestamp:!1,showTrendLine:!1,startYAxisAtZero:!0,subheader:"",subheaderFontSize:PROPORTION.SUBHEADER,timeRangeFixed:!1};const _default=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_8__.iK)(BigNumberVis)`
  font-family: ${({theme:e})=>e.typography.families.sansSerif};
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;

  &.no-trendline .subheader-line {
    padding-bottom: 0.3em;
  }

  .text-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    .alert {
      font-size: ${({theme:e})=>e.typography.sizes.s};
      margin: -0.5em 0 0.4em;
      line-height: 1;
      padding: 2px 4px 3px;
      border-radius: 3px;
    }
  }

  .kicker {
    font-weight: ${({theme:e})=>e.typography.weights.light};
    line-height: 1em;
    padding-bottom: 2em;
  }

  .header-line {
    font-weight: ${({theme:e})=>e.typography.weights.normal};
    position: relative;
    line-height: 1em;
    span {
      position: absolute;
      bottom: 0;
    }
  }

  .subheader-line {
    font-weight: ${({theme:e})=>e.typography.weights.light};
    line-height: 1em;
    padding-bottom: 0;
  }

  &.is-fallback-value {
    .kicker,
    .header-line,
    .subheader-line {
      opacity: 0.5;
    }
  }

  .superset-data-ui-tooltip {
    z-index: 1000;
    background: #000;
  }
`,__WEBPACK_DEFAULT_EXPORT__=_default;var reactHotLoader,leaveModule;reactHotLoader="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0,reactHotLoader&&(reactHotLoader.register(defaultNumberFormatter,"defaultNumberFormatter","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx"),reactHotLoader.register(PROPORTION,"PROPORTION","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx"),reactHotLoader.register(BigNumberVis,"BigNumberVis","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx"),reactHotLoader.register(_default,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx")),leaveModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0,leaveModule&&leaveModule(module)},263475:(e,t,r)=>{r.d(t,{Z:()=>d});var _,a=r(667294),n=r(751995),i=r(229027),s=r(211965);e=r.hmd(e),(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&_(e);var o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const c=n.iK.div`
  height: ${({height:e})=>e};
  width: ${({width:e})=>e};
`;function u({width:e,height:t,echartOptions:r,eventHandlers:_,zrEventHandlers:n,selectedValues:o={}},u){const l=(0,a.useRef)(null),d=(0,a.useRef)(),h=(0,a.useMemo)((()=>Object.keys(o)||[]),[o]),p=(0,a.useRef)([]);return(0,a.useImperativeHandle)(u,(()=>({getEchartInstance:()=>d.current}))),(0,a.useEffect)((()=>{l.current&&(d.current||(d.current=(0,i.S1)(l.current)),Object.entries(_||{}).forEach((([e,t])=>{var r,_;null==(r=d.current)||r.off(e),null==(_=d.current)||_.on(e,t)})),Object.entries(n||{}).forEach((([e,t])=>{var r,_;null==(r=d.current)||r.getZr().off(e),null==(_=d.current)||_.getZr().on(e,t)})),d.current.setOption(r,!0))}),[r,_,n]),(0,a.useEffect)((()=>{d.current&&(d.current.dispatchAction({type:"downplay",dataIndex:p.current.filter((e=>!h.includes(e)))}),h.length&&d.current.dispatchAction({type:"highlight",dataIndex:h}),p.current=h)}),[h]),(0,a.useEffect)((()=>{d.current&&d.current.resize({width:e,height:t})}),[e,t]),(0,s.tZ)(c,{ref:l,height:t,width:e})}o(u,"useRef{divRef}\nuseRef{chartRef}\nuseMemo{currentSelection}\nuseRef{previousSelection}\nuseImperativeHandle{}\nuseEffect{}\nuseEffect{}\nuseEffect{}",(()=>[a.useImperativeHandle]));const l=(0,a.forwardRef)(u),d=l;var h,p;(h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(h.register(c,"Styles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/components/Echart.tsx"),h.register(u,"Echart","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/components/Echart.tsx"),h.register(l,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/plugins/plugin-chart-echarts/src/components/Echart.tsx")),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&p(e)}}]);