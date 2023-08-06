(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[9083],{313433:(module,__webpack_exports__,__webpack_require__)=>{"use strict";__webpack_require__.d(__webpack_exports__,{Z:()=>__WEBPACK_DEFAULT_EXPORT__});var react__WEBPACK_IMPORTED_MODULE_0__=__webpack_require__(667294),prop_types__WEBPACK_IMPORTED_MODULE_1__=__webpack_require__(45697),prop_types__WEBPACK_IMPORTED_MODULE_1___default=__webpack_require__.n(prop_types__WEBPACK_IMPORTED_MODULE_1__),_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__=__webpack_require__(455867),src_components_Tooltip__WEBPACK_IMPORTED_MODULE_2__=__webpack_require__(358593),src_components_MessageToasts_withToasts__WEBPACK_IMPORTED_MODULE_3__=__webpack_require__(414114),src_utils_copy__WEBPACK_IMPORTED_MODULE_4__=__webpack_require__(710222),_emotion_react__WEBPACK_IMPORTED_MODULE_5__=__webpack_require__(211965),enterModule;function _EMOTION_STRINGIFIED_CSS_ERROR__(){return"You have tried to stringify object returned from `css` function. It isn't supposed to be used directly (e.g. as value of the `className` prop), but rather handed to emotion so it can handle it (e.g. as value of `css` prop)."}module=__webpack_require__.hmd(module),enterModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0,enterModule&&enterModule(module);var __signature__="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const propTypes={copyNode:prop_types__WEBPACK_IMPORTED_MODULE_1___default().node,getText:prop_types__WEBPACK_IMPORTED_MODULE_1___default().func,onCopyEnd:prop_types__WEBPACK_IMPORTED_MODULE_1___default().func,shouldShowText:prop_types__WEBPACK_IMPORTED_MODULE_1___default().bool,text:prop_types__WEBPACK_IMPORTED_MODULE_1___default().string,wrapped:prop_types__WEBPACK_IMPORTED_MODULE_1___default().bool,tooltipText:prop_types__WEBPACK_IMPORTED_MODULE_1___default().string,addDangerToast:prop_types__WEBPACK_IMPORTED_MODULE_1___default().func.isRequired,addSuccessToast:prop_types__WEBPACK_IMPORTED_MODULE_1___default().func.isRequired},defaultProps={copyNode:(0,_emotion_react__WEBPACK_IMPORTED_MODULE_5__.tZ)("span",null,"Copy"),onCopyEnd:()=>{},shouldShowText:!0,wrapped:!0,tooltipText:(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__.t)("Copy to clipboard")};var _ref={name:"8irbms",styles:"display:inline-flex;align-items:center"};class CopyToClipboard extends react__WEBPACK_IMPORTED_MODULE_0__.Component{constructor(e){super(e),this.copyToClipboard=this.copyToClipboard.bind(this),this.onClick=this.onClick.bind(this)}onClick(){this.props.getText?this.props.getText((e=>{this.copyToClipboard(e)})):this.copyToClipboard(this.props.text)}getDecoratedCopyNode(){return react__WEBPACK_IMPORTED_MODULE_0__.cloneElement(this.props.copyNode,{style:{cursor:"pointer"},onClick:this.onClick})}copyToClipboard(e){(0,src_utils_copy__WEBPACK_IMPORTED_MODULE_4__.Z)(e).then((()=>{this.props.addSuccessToast((0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__.t)("Copied to clipboard!"))})).catch((()=>{this.props.addDangerToast((0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_6__.t)("Sorry, your browser does not support copying. Use Ctrl / Cmd + C!"))})).finally((()=>{this.props.onCopyEnd()}))}renderNotWrapped(){return(0,_emotion_react__WEBPACK_IMPORTED_MODULE_5__.tZ)(src_components_Tooltip__WEBPACK_IMPORTED_MODULE_2__.u,{id:"copy-to-clipboard-tooltip",placement:"top",style:{cursor:"pointer"},title:this.props.tooltipText,trigger:["hover"]},this.getDecoratedCopyNode())}renderLink(){return(0,_emotion_react__WEBPACK_IMPORTED_MODULE_5__.tZ)("span",{css:_ref},this.props.shouldShowText&&this.props.text&&(0,_emotion_react__WEBPACK_IMPORTED_MODULE_5__.tZ)("span",{className:"m-r-5","data-test":"short-url"},this.props.text),(0,_emotion_react__WEBPACK_IMPORTED_MODULE_5__.tZ)(src_components_Tooltip__WEBPACK_IMPORTED_MODULE_2__.u,{id:"copy-to-clipboard-tooltip",placement:"top",title:this.props.tooltipText,trigger:["hover"]},this.getDecoratedCopyNode()))}render(){const{wrapped:e}=this.props;return e?this.renderLink():this.renderNotWrapped()}__reactstandin__regenerateByEval(key,code){this[key]=eval(code)}}const _default=(0,src_components_MessageToasts_withToasts__WEBPACK_IMPORTED_MODULE_3__.Z)(CopyToClipboard),__WEBPACK_DEFAULT_EXPORT__=_default;var reactHotLoader,leaveModule;CopyToClipboard.propTypes=propTypes,CopyToClipboard.defaultProps=defaultProps,reactHotLoader="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0,reactHotLoader&&(reactHotLoader.register(propTypes,"propTypes","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/CopyToClipboard/index.jsx"),reactHotLoader.register(defaultProps,"defaultProps","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/CopyToClipboard/index.jsx"),reactHotLoader.register(CopyToClipboard,"CopyToClipboard","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/CopyToClipboard/index.jsx"),reactHotLoader.register(_default,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/CopyToClipboard/index.jsx")),leaveModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0,leaveModule&&leaveModule(module)},454076:(e,t,r)=>{"use strict";r.d(t,{li:()=>i,Tb:()=>c,jy:()=>u,G9:()=>_,lo:()=>g,Mv:()=>v,cD:()=>h,EI:()=>f,fV:()=>b});var o,s=r(435778),n=r(642846),a=r(431069),l=r(355786);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const d="<empty string>",i="<NULL>",c="TRUE",u="FALSE",p=(0,s.bt)(n.Z.DATABASE_DATETIME);function _(e){return a.Z.post({endpoint:"/kv/store/",postPayload:{data:e}}).then((e=>`${window.location.origin+window.location.pathname}?id=${e.json.id}`))}function g(e){return null===e?i:""===e?d:!0===e?"<true>":!1===e?"<false>":"string"!=typeof e&&e.toString?e.toString():e}function m(e){return null===e?i:e}function v(e,t){let r="";for(let o=0;o<e.length;o+=1){const s={};for(let r=0;r<t.length;r+=1){const n=t[r].name||t[r];e[o][n]?s[r]=e[o][n]:s[r]=e[o][parseFloat(n)]}r+=`${Object.values(s).join("\t")}\n`}return r}function h(e,t){return e&&0!==e.length&&0!==(0,l.Z)(t).length?e.map((e=>({...e,...t.reduce(((t,r)=>(null!==e[r]&&void 0!==e[r]&&(t[r]=p(e[r])),t)),{})}))):e}const f=()=>{},b=()=>{const{appVersion:e}=navigator;return e.includes("Win")?"Windows":e.includes("Mac")?"MacOS":e.includes("X11")?"UNIX":e.includes("Linux")?"Linux":"Unknown OS"};var E,R;(E="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(E.register(d,"EMPTY_STRING","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(i,"NULL_STRING","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(c,"TRUE_STRING","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(u,"FALSE_STRING","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register("MMM D, YYYY","SHORT_DATE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register("h:m a","SHORT_TIME","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(p,"DATETIME_FORMATTER","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register((function(e,t){const r=e.split("&");for(let e=0;e<r.length;e+=1){const o=r[e].split("=");if(decodeURIComponent(o[0])===t)return decodeURIComponent(o[1])}return null}),"getParamFromQuery","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(_,"storeQuery","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(g,"optionLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(m,"optionValue","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register((function(e){return{value:m(e),label:g(e)}}),"optionFromValue","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(v,"prepareCopyToClipboardTabularData","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(h,"applyFormattingToTabularData","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(f,"noOp","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js"),E.register(b,"detectOS","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/common.js")),(R="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&R(e)},355786:(e,t,r)=>{"use strict";var o,s,n;function a(e){return null==e?[]:Array.isArray(e)?e:[e]}r.d(t,{Z:()=>a}),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature,(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&s.register(a,"ensureIsArray","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/packages/superset-ui-core/src/utils/ensureIsArray.ts"),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)},582191:(e,t,r)=>{"use strict";r.d(t,{Qc:()=>_.Z,qE:()=>g.C,zx:()=>m.Z,XZ:()=>v.Z,JX:()=>h.Z,iz:()=>f.Z,Lt:()=>c.Z,l0:()=>b.Z,rj:()=>E.ZP,HY:()=>R.Z,ZT:()=>y.Z,mp:()=>O.Z,iR:()=>T.Z,X2:()=>L.Z,T:()=>P.Z,Od:()=>u.Z,Rg:()=>C.Z,rs:()=>M.Z,Vp:()=>x.Z,mQ:()=>A.Z,u:()=>N.Z,gq:()=>I.Z,oc:()=>d.Z,Ak:()=>H.Z,u_:()=>D.Z,bZ:()=>G.default,Ph:()=>S.default,aV:()=>U.default,UO:()=>k.Z,v2:()=>$,$t:()=>B,II:()=>W,Rn:()=>K,Kx:()=>F,$i:()=>z,yX:()=>V});var o,s=r(205872),n=r.n(s),a=(r(667294),r(751995)),l=r(743865),d=r(804107),i=r(121888),c=r(216114),u=r(133860),p=r(211965),_=r(449288),g=r(751890),m=r(360404),v=r(609676),h=r(515746),f=r(227049),b=r(7646),E=r(75302),R=r(814277),y=r(59118),O=r(231183),T=r(231955),L=r(771230),P=r(519650),C=r(627220),M=r(359314),x=r(560331),A=r(488108),N=r(931097),I=r(176310),H=r(339144),D=r(256697),G=r(404863),S=r(564749),U=r(56590),k=r(843700);r(782607),r(657011),r(367135),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const Z=(0,a.iK)(l.Z.Item)`
  > a {
    text-decoration: none;
  }

  &.ant-menu-item {
    height: ${({theme:e})=>7*e.gridUnit}px;
    line-height: ${({theme:e})=>7*e.gridUnit}px;
    a {
      border-bottom: none;
      transition: background-color ${({theme:e})=>e.transitionTiming}s;
      &:after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 50%;
        width: 0;
        height: 3px;
        opacity: 0;
        transform: translateX(-50%);
        transition: all ${({theme:e})=>e.transitionTiming}s;
        background-color: ${({theme:e})=>e.colors.primary.base};
      }
      &:focus {
        border-bottom: none;
        background-color: transparent;
        @media (max-width: 767px) {
          background-color: ${({theme:e})=>e.colors.primary.light5};
        }
      }
    }
  }

  &.ant-menu-item,
  &.ant-dropdown-menu-item {
    span[role='button'] {
      display: inline-block;
      width: 100%;
    }
    transition-duration: 0s;
  }
`,j=(0,a.iK)(l.Z)`
  line-height: 51px;
  border: none;

  & > .ant-menu-item,
  & > .ant-menu-submenu {
    vertical-align: inherit;
    &:hover {
      color: ${({theme:e})=>e.colors.grayscale.dark1};
    }
  }

  &:not(.ant-menu-dark) > .ant-menu-submenu,
  &:not(.ant-menu-dark) > .ant-menu-item {
    &:hover {
      border-bottom: none;
    }
  }

  &:not(.ant-menu-dark) > .ant-menu-submenu,
  &:not(.ant-menu-dark) > .ant-menu-item {
    margin: 0px;
  }

  & > .ant-menu-item > a {
    padding: ${({theme:e})=>4*e.gridUnit}px;
  }
`,w=(0,a.iK)(l.Z.SubMenu)`
  color: ${({theme:e})=>e.colors.grayscale.dark1};
  border-bottom: none;
  .ant-menu-submenu-open,
  .ant-menu-submenu-active {
    background-color: ${({theme:e})=>e.colors.primary.light5};
    .ant-menu-submenu-title {
      color: ${({theme:e})=>e.colors.grayscale.dark1};
      background-color: ${({theme:e})=>e.colors.primary.light5};
      border-bottom: none;
      margin: 0;
      &:after {
        opacity: 1;
        width: calc(100% - 1);
      }
    }
  }
  .ant-menu-submenu-title {
    position: relative;
    top: ${({theme:e})=>-e.gridUnit-3}px;
    &:after {
      content: '';
      position: absolute;
      bottom: -3px;
      left: 50%;
      width: 0;
      height: 3px;
      opacity: 0;
      transform: translateX(-50%);
      transition: all ${({theme:e})=>e.transitionTiming}s;
      background-color: ${({theme:e})=>e.colors.primary.base};
    }
  }
  .ant-menu-submenu-arrow {
    top: 67%;
  }
  & > .ant-menu-submenu-title {
    padding: 0 ${({theme:e})=>6*e.gridUnit}px 0
      ${({theme:e})=>3*e.gridUnit}px !important;
    span[role='img'] {
      position: absolute;
      right: ${({theme:e})=>-e.gridUnit-2}px;
      top: ${({theme:e})=>5.25*e.gridUnit}px;
      svg {
        font-size: ${({theme:e})=>6*e.gridUnit}px;
        color: ${({theme:e})=>e.colors.grayscale.base};
      }
    }
    & > span {
      position: relative;
      top: 7px;
    }
    &:hover {
      color: ${({theme:e})=>e.colors.primary.base};
    }
  }
`,$=Object.assign(l.Z,{Item:Z}),B=Object.assign(j,{Item:Z,SubMenu:w,Divider:l.Z.Divider,ItemGroup:l.Z.ItemGroup}),W=(0,a.iK)(d.Z)`
  border: 1px solid ${({theme:e})=>e.colors.secondary.light3};
  border-radius: ${({theme:e})=>e.borderRadius}px;
`,K=(0,a.iK)(i.Z)`
  border: 1px solid ${({theme:e})=>e.colors.secondary.light3};
  border-radius: ${({theme:e})=>e.borderRadius}px;
`,F=(0,a.iK)(d.Z.TextArea)`
  border: 1px solid ${({theme:e})=>e.colors.secondary.light3};
  border-radius: ${({theme:e})=>e.borderRadius}px;
`,z=e=>(0,p.tZ)(c.Z,n()({overlayStyle:{zIndex:99,animationDuration:"0s"}},e)),V=(0,a.iK)(u.Z)`
  h3 {
    margin: ${({theme:e})=>e.gridUnit}px 0;
  }

  ul {
    margin-bottom: 0;
  }
`;var Y,q;(Y="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(Y.register(Z,"MenuItem","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(j,"StyledNav","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(w,"StyledSubMenu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register($,"Menu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(B,"MainNav","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(W,"Input","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(K,"InputNumber","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(F,"TextArea","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(z,"NoAnimationDropdown","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx"),Y.register(V,"ThinSkeleton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/common/components/index.tsx")),(q="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&q(e)},782607:(e,t,r)=>{"use strict";r.d(t,{Z:()=>i}),r(667294);var o,s=r(751995),n=r(762529),a=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const l=(0,s.iK)((({textColor:e,...t})=>(0,a.tZ)(n.Z,t)))`
  & > sup {
    padding: 0 ${({theme:e})=>2*e.gridUnit}px;
    background: ${({theme:e,color:t})=>t||e.colors.primary.base};
    color: ${({theme:e,textColor:t})=>t||e.colors.grayscale.light5};
  }
`,d=l,i=d;var c,u;(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(c.register(l,"Badge","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Badge/index.tsx"),c.register(d,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Badge/index.tsx")),(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&u(e)},835932:(e,t,r)=>{"use strict";r.d(t,{Z:()=>f});var o,s,n,a=r(205872),l=r.n(a),d=r(211965),i=r(121804),c=r.n(i),u=r(667294),p=r(884967),_=r(294184),g=r.n(_),m=r(360404),v=r(751995),h=r(358593);function f(e){const{tooltip:t,placement:r,disabled:o=!1,buttonSize:s,buttonStyle:n,className:a,cta:i,children:_,href:f,showMarginRight:b=!0,...E}=e,R=(0,v.Fg)(),{colors:y,transitionTiming:O,borderRadius:T,typography:L}=R,{primary:P,grayscale:C,success:M,warning:x,error:A}=y;let N=32,I=18;"xsmall"===s?(N=22,I=5):"small"===s&&(N=30,I=10);let H=P.light4,D=(0,p.CD)(.1,P.base,P.light4),G=(0,p.CD)(.25,P.base,P.light4),S=C.light2,U=P.dark1,k=U,Z=0,j="none",w="transparent",$="transparent",B="transparent";"primary"===n?(H=P.dark1,D=(0,p.CD)(.1,C.light5,P.dark1),G=(0,p.CD)(.2,C.dark2,P.dark1),U=C.light5,k=U):"tertiary"===n||"dashed"===n?(H=C.light5,D=C.light5,G=C.light5,S=C.light5,Z=1,j="dashed"===n?"dashed":"solid",w=P.dark1,$=P.light1,B=C.light2):"danger"===n?(H=A.base,D=(0,p.CD)(.1,C.light5,A.base),G=(0,p.CD)(.2,C.dark2,A.base),U=C.light5,k=U):"warning"===n?(H=x.base,D=(0,p.CD)(.1,C.dark2,x.base),G=(0,p.CD)(.2,C.dark2,x.base),U=C.light5,k=U):"success"===n?(H=M.base,D=(0,p.CD)(.1,C.light5,M.base),G=(0,p.CD)(.2,C.dark2,M.base),U=C.light5,k=U):"link"===n&&(H="transparent",D="transparent",G="transparent",k=P.base);const W=_;let K=[];K=W&&W.type===u.Fragment?u.Children.toArray(W.props.children):u.Children.toArray(_);const F=b&&K.length>1?2*R.gridUnit:0,z=(0,d.tZ)(m.Z,l()({href:o?void 0:f,disabled:o,className:g()(a,"superset-button",{cta:!!i}),css:(0,d.iv)({display:"inline-flex",alignItems:"center",justifyContent:"center",lineHeight:1.5715,fontSize:L.sizes.s,fontWeight:L.weights.bold,height:N,textTransform:"uppercase",padding:`0px ${I}px`,transition:`all ${O}s`,minWidth:i?36*R.gridUnit:void 0,minHeight:i?8*R.gridUnit:void 0,boxShadow:"none",borderWidth:Z,borderStyle:j,borderColor:w,borderRadius:T,color:U,backgroundColor:H,"&:hover":{color:k,backgroundColor:D,borderColor:$},"&:active":{color:U,backgroundColor:G},"&:focus":{color:U,backgroundColor:H,borderColor:w},"&[disabled], &[disabled]:hover":{color:C.base,backgroundColor:S,borderColor:B},marginLeft:0,"& + .superset-button":{marginLeft:2*R.gridUnit},"& :first-of-type":{marginRight:F}},"","")},E),_);return t?(0,d.tZ)(h.u,{placement:r,id:`${c()(t)}-tooltip`,title:t},o?(0,d.tZ)("span",null,z):z):z}e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),("undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e})(f,"useTheme{theme}",(()=>[v.Fg])),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&s.register(f,"Button","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Button/index.tsx"),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)},657011:(e,t,r)=>{"use strict";r.d(t,{Z:()=>c});var o,s=r(205872),n=r.n(s),a=(r(667294),r(570302)),l=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const d=({padded:e,...t})=>(0,l.tZ)(a.Z,n()({},t,{css:t=>({backgroundColor:t.colors.grayscale.light4,borderRadius:t.borderRadius,".ant-card-body":{padding:e?4*t.gridUnit:t.gridUnit}})})),i=d,c=i;var u,p;(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(u.register(d,"Card","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Card/index.tsx"),u.register(i,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Card/index.tsx")),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&p(e)},843700:(e,t,r)=>{"use strict";r.d(t,{Z:()=>i}),r(667294);var o,s=r(751995),n=r(46445),a=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const l=Object.assign((0,s.iK)((({light:e,bigger:t,bold:r,animateArrows:o,...s})=>(0,a.tZ)(n.Z,s)))`
    .ant-collapse-item {
      .ant-collapse-header {
        font-weight: ${({bold:e,theme:t})=>e?t.typography.weights.bold:t.typography.weights.normal};
        font-size: ${({bigger:e,theme:t})=>e?4*t.gridUnit+"px":"inherit"};

        .ant-collapse-arrow svg {
          transition: ${({animateArrows:e})=>e?"transform 0.24s":"none"};
        }

        ${({expandIconPosition:e})=>e&&"right"===e&&"\n            .anticon.anticon-right.ant-collapse-arrow > svg {\n              transform: rotate(90deg) !important;\n            }\n          "}

        ${({light:e,theme:t})=>e&&`\n            color: ${t.colors.grayscale.light4};\n            .ant-collapse-arrow svg {\n              color: ${t.colors.grayscale.light4};\n            }\n          `}

        ${({ghost:e,bordered:t,theme:r})=>e&&t&&`\n            border-bottom: 1px solid ${r.colors.grayscale.light3};\n          `}
      }
      .ant-collapse-content {
        .ant-collapse-content-box {
          .loading.inline {
            margin: ${({theme:e})=>12*e.gridUnit}px auto;
            display: block;
          }
        }
      }
    }
    .ant-collapse-item-active {
      .ant-collapse-header {
        ${({expandIconPosition:e})=>e&&"right"===e&&"\n            .anticon.anticon-right.ant-collapse-arrow > svg {\n              transform: rotate(-90deg) !important;\n            }\n          "}
      }
    }
  `,{Panel:n.Z.Panel}),d=l,i=d;var c,u;(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(c.register(l,"Collapse","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Collapse/index.tsx"),c.register(d,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Collapse/index.tsx")),(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&u(e)},891178:(e,t,r)=>{"use strict";r.d(t,{Z:()=>h});var o,s=r(667294),n=r(751995),a=r(455867),l=r(454076),d=r(574520),i=r(835932),c=r(87693),u=r(313433),p=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e);var _="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const g=n.iK.div`
  align-items: center;
  background-color: ${({level:e,theme:t})=>t.colors[e].light2};
  border-radius: ${({theme:e})=>e.borderRadius}px;
  border: 1px solid ${({level:e,theme:t})=>t.colors[e].base};
  color: ${({level:e,theme:t})=>t.colors[e].dark2};
  padding: ${({theme:e})=>2*e.gridUnit}px;
  width: 100%;

  .top-row {
    display: flex;
    justify-content: space-between;
  }

  .error-body {
    padding-top: ${({theme:e})=>e.gridUnit}px;
    padding-left: ${({theme:e})=>8*e.gridUnit}px;
  }

  .icon {
    margin-right: ${({theme:e})=>2*e.gridUnit}px;
  }

  .link {
    color: ${({level:e,theme:t})=>t.colors[e].dark2};
    text-decoration: underline;
  }
`,m=(0,n.iK)(d.Z)`
  color: ${({level:e,theme:t})=>t.colors[e].dark2};
  overflow-wrap: break-word;

  .ant-modal-header {
    background-color: ${({level:e,theme:t})=>t.colors[e].light2};
    padding: ${({theme:e})=>4*e.gridUnit}px;
  }

  .icon {
    margin-right: ${({theme:e})=>2*e.gridUnit}px;
  }

  .header {
    display: flex;
    align-items: center;
    font-size: ${({theme:e})=>e.typography.sizes.l}px;
  }
`,v=n.iK.div`
  align-items: center;
  display: flex;
`;function h({body:e,copyText:t,level:r="error",source:o="dashboard",subtitle:d,title:_}){const h=(0,n.Fg)(),[f,b]=(0,s.useState)(!1),[E,R]=(0,s.useState)(!1),y=["explore","sqllab"].includes(o),O=h.colors[r].base;return(0,p.tZ)(g,{level:r,role:"alert"},(0,p.tZ)("div",{className:"top-row"},(0,p.tZ)(v,null,"error"===r?(0,p.tZ)(c.Z.ErrorSolid,{className:"icon",iconColor:O}):(0,p.tZ)(c.Z.WarningSolid,{className:"icon",iconColor:O}),(0,p.tZ)("strong",null,_)),!y&&(0,p.tZ)("span",{role:"button",tabIndex:0,className:"link",onClick:()=>b(!0)},(0,a.t)("See more"))),y?(0,p.tZ)("div",{className:"error-body"},(0,p.tZ)("p",null,d),e&&(0,p.tZ)(s.Fragment,null,!E&&(0,p.tZ)("span",{role:"button",tabIndex:0,className:"link",onClick:()=>R(!0)},(0,a.t)("See more")),E&&(0,p.tZ)(s.Fragment,null,(0,p.tZ)("br",null),e,(0,p.tZ)("span",{role:"button",tabIndex:0,className:"link",onClick:()=>R(!1)},(0,a.t)("See less"))))):(0,p.tZ)(m,{level:r,show:f,onHide:()=>b(!1),title:(0,p.tZ)("div",{className:"header"},"error"===r?(0,p.tZ)(c.Z.ErrorSolid,{className:"icon",iconColor:O}):(0,p.tZ)(c.Z.WarningSolid,{className:"icon",iconColor:O}),(0,p.tZ)("div",{className:"title"},_)),footer:(0,p.tZ)(s.Fragment,null,t&&(0,p.tZ)(u.Z,{text:t,shouldShowText:!1,wrapped:!1,copyNode:(0,p.tZ)(i.Z,{onClick:l.EI},(0,a.t)("Copy message"))}),(0,p.tZ)(i.Z,{cta:!0,buttonStyle:"primary",onClick:()=>b(!1)},(0,a.t)("Close")))},(0,p.tZ)(s.Fragment,null,(0,p.tZ)("p",null,d),(0,p.tZ)("br",null),e)))}var f,b;_(h,"useTheme{theme}\nuseState{[isModalOpen, setIsModalOpen](false)}\nuseState{[isBodyExpanded, setIsBodyExpanded](false)}",(()=>[n.Fg])),(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(f.register(g,"ErrorAlertDiv","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/ErrorAlert.tsx"),f.register(m,"ErrorModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/ErrorAlert.tsx"),f.register(v,"LeftSideContent","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/ErrorAlert.tsx"),f.register(h,"ErrorAlert","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/ErrorAlert.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},792869:(module,__webpack_exports__,__webpack_require__)=>{"use strict";__webpack_require__.d(__webpack_exports__,{Z:()=>__WEBPACK_DEFAULT_EXPORT__});var _superset_ui_core__WEBPACK_IMPORTED_MODULE_0__=__webpack_require__(590537),_superset_ui_core__WEBPACK_IMPORTED_MODULE_1__=__webpack_require__(601875),enterModule;module=__webpack_require__.hmd(module),enterModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0,enterModule&&enterModule(module);var __signature__="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};class ErrorMessageComponentRegistry extends _superset_ui_core__WEBPACK_IMPORTED_MODULE_0__.Z{constructor(){super({name:"ErrorMessageComponent",overwritePolicy:_superset_ui_core__WEBPACK_IMPORTED_MODULE_0__.r.ALLOW})}__reactstandin__regenerateByEval(key,code){this[key]=eval(code)}}const getErrorMessageComponentRegistry=(0,_superset_ui_core__WEBPACK_IMPORTED_MODULE_1__.Z)(ErrorMessageComponentRegistry),_default=getErrorMessageComponentRegistry,__WEBPACK_DEFAULT_EXPORT__=_default;var reactHotLoader,leaveModule;reactHotLoader="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0,reactHotLoader&&(reactHotLoader.register(ErrorMessageComponentRegistry,"ErrorMessageComponentRegistry","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/getErrorMessageComponentRegistry.ts"),reactHotLoader.register(getErrorMessageComponentRegistry,"getErrorMessageComponentRegistry","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/getErrorMessageComponentRegistry.ts"),reactHotLoader.register(_default,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/getErrorMessageComponentRegistry.ts")),leaveModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0,leaveModule&&leaveModule(module)},167663:(e,t,r)=>{"use strict";var o;r.d(t,{C:()=>s}),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const s={FRONTEND_CSRF_ERROR:"FRONTEND_CSRF_ERROR",FRONTEND_NETWORK_ERROR:"FRONTEND_NETWORK_ERROR",FRONTEND_TIMEOUT_ERROR:"FRONTEND_TIMEOUT_ERROR",GENERIC_DB_ENGINE_ERROR:"GENERIC_DB_ENGINE_ERROR",COLUMN_DOES_NOT_EXIST_ERROR:"COLUMN_DOES_NOT_EXIST_ERROR",TABLE_DOES_NOT_EXIST_ERROR:"TABLE_DOES_NOT_EXIST_ERROR",SCHEMA_DOES_NOT_EXIST_ERROR:"SCHEMA_DOES_NOT_EXIST_ERROR",CONNECTION_INVALID_USERNAME_ERROR:"CONNECTION_INVALID_USERNAME_ERROR",CONNECTION_INVALID_PASSWORD_ERROR:"CONNECTION_INVALID_PASSWORD_ERROR",CONNECTION_INVALID_HOSTNAME_ERROR:"CONNECTION_INVALID_HOSTNAME_ERROR",CONNECTION_PORT_CLOSED_ERROR:"CONNECTION_PORT_CLOSED_ERROR",CONNECTION_INVALID_PORT_ERROR:"CONNECTION_INVALID_PORT_ERROR",CONNECTION_HOST_DOWN_ERROR:"CONNECTION_HOST_DOWN_ERROR",CONNECTION_ACCESS_DENIED_ERROR:"CONNECTION_ACCESS_DENIED_ERROR",CONNECTION_UNKNOWN_DATABASE_ERROR:"CONNECTION_UNKNOWN_DATABASE_ERROR",CONNECTION_DATABASE_PERMISSIONS_ERROR:"CONNECTION_DATABASE_PERMISSIONS_ERROR",CONNECTION_MISSING_PARAMETERS_ERRORS:"CONNECTION_MISSING_PARAMETERS_ERRORS",OBJECT_DOES_NOT_EXIST_ERROR:"OBJECT_DOES_NOT_EXIST_ERROR",SYNTAX_ERROR:"SYNTAX_ERROR",VIZ_GET_DF_ERROR:"VIZ_GET_DF_ERROR",UNKNOWN_DATASOURCE_TYPE_ERROR:"UNKNOWN_DATASOURCE_TYPE_ERROR",FAILED_FETCHING_DATASOURCE_INFO_ERROR:"FAILED_FETCHING_DATASOURCE_INFO_ERROR",TABLE_SECURITY_ACCESS_ERROR:"TABLE_SECURITY_ACCESS_ERROR",DATASOURCE_SECURITY_ACCESS_ERROR:"DATASOURCE_SECURITY_ACCESS_ERROR",DATABASE_SECURITY_ACCESS_ERROR:"DATABASE_SECURITY_ACCESS_ERROR",QUERY_SECURITY_ACCESS_ERROR:"QUERY_SECURITY_ACCESS_ERROR",MISSING_OWNERSHIP_ERROR:"MISSING_OWNERSHIP_ERROR",BACKEND_TIMEOUT_ERROR:"BACKEND_TIMEOUT_ERROR",DATABASE_NOT_FOUND_ERROR:"DATABASE_NOT_FOUND_ERROR",MISSING_TEMPLATE_PARAMS_ERROR:"MISSING_TEMPLATE_PARAMS_ERROR",INVALID_TEMPLATE_PARAMS_ERROR:"INVALID_TEMPLATE_PARAMS_ERROR",RESULTS_BACKEND_NOT_CONFIGURED_ERROR:"RESULTS_BACKEND_NOT_CONFIGURED_ERROR",DML_NOT_ALLOWED_ERROR:"DML_NOT_ALLOWED_ERROR",INVALID_CTAS_QUERY_ERROR:"INVALID_CTAS_QUERY_ERROR",INVALID_CVAS_QUERY_ERROR:"INVALID_CVAS_QUERY_ERROR",SQLLAB_TIMEOUT_ERROR:"SQLLAB_TIMEOUT_ERROR",RESULTS_BACKEND_ERROR:"RESULTS_BACKEND_ERROR",ASYNC_WORKERS_ERROR:"ASYNC_WORKERS_ERROR",GENERIC_COMMAND_ERROR:"GENERIC_COMMAND_ERROR",GENERIC_BACKEND_ERROR:"GENERIC_BACKEND_ERROR",INVALID_PAYLOAD_FORMAT_ERROR:"INVALID_PAYLOAD_FORMAT_ERROR",INVALID_PAYLOAD_SCHEMA_ERROR:"INVALID_PAYLOAD_SCHEMA_ERROR"};var n,a;(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&n.register(s,"ErrorTypeEnum","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ErrorMessage/types.ts"),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&a(e)},184913:(e,t,r)=>{"use strict";r.d(t,{Z:()=>u});var o,s=r(205872),n=r.n(s),a=(r(667294),r(362816)),l=r(210573),d=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const i=Object.keys(a).map((e=>({[e]:t=>(0,d.tZ)(l.xL,n()({component:a[e]},t))}))).reduce(((e,t)=>({...e,...t}))),c=i,u=c;var p,_;(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(p.register(i,"AntdEnhancedIcons","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/AntdEnhanced.tsx"),p.register(c,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/AntdEnhanced.tsx")),(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&_(e)},210573:(e,t,r)=>{"use strict";r.d(t,{xL:()=>g,ZP:()=>h});var o=r(205872),s=r.n(o),n=(r(115306),r(667294)),a=r(316165),l=r(751995);function d(){return d=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var o in r)Object.prototype.hasOwnProperty.call(r,o)&&(e[o]=r[o])}return e},d.apply(this,arguments)}const i=function(e){return n.createElement("svg",d({width:24,height:24,viewBox:"0 0 24 24",fill:"none",xmlns:"http://www.w3.org/2000/svg"},e))};var c,u=r(211965);e=r.hmd(e),(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&c(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const _=({iconColor:e,iconSize:t,viewBox:r,...o})=>(0,u.tZ)(a.Z,s()({viewBox:r||"0 0 24 24"},o)),g=(0,l.iK)(_)`
  ${({iconColor:e})=>e&&`color: ${e};`};
  font-size: ${({iconSize:e,theme:t})=>e?`${t.typography.sizes[e]||t.typography.sizes.m}px`:"24px"};
`,m=e=>{const{fileName:t,...o}=e,[,a]=(0,n.useState)(!1),l=(0,n.useRef)(),d=t.replace("_","-");return(0,n.useEffect)((()=>{let e=!1;return async function(){l.current=(await r(335782)(`./${t}.svg`)).default,e||a(!0)}(),()=>{e=!0}}),[t,l]),(0,u.tZ)(g,s()({component:l.current||i,"aria-label":d},o))};p(m,"useState{[, setLoaded](false)}\nuseRef{ImportedSVG}\nuseEffect{}");const v=m,h=v;var f,b;(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(f.register(_,"AntdIconComponent","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/Icon.tsx"),f.register(g,"StyledIcon","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/Icon.tsx"),f.register(m,"Icon","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/Icon.tsx"),f.register(v,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/Icon.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},87693:(e,t,r)=>{"use strict";r.d(t,{Z:()=>g});var o,s=r(205872),n=r.n(s),a=r(318029),l=r.n(a),d=(r(115306),r(667294),r(184913)),i=r(210573),c=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const u=["alert","alert_solid","alert_solid_small","binoculars","bolt","bolt_small","bolt_small_run","calendar","cancel","cancel_solid","cancel-x","card_view","cards","cards_locked","caret_down","caret_left","caret_right","caret_up","certified","check","checkbox-half","checkbox-off","checkbox-on","circle_check","circle_check_solid","circle","clock","close","code","cog","collapse","color_palette","components","copy","cursor_target","database","dataset_physical","dataset_virtual_greyscale","dataset_virtual","download","drag","edit_alt","edit","email","error","error_solid","error_solid_small","exclamation","expand","eye","eye_slash","favorite-selected","favorite_small_selected","favorite-unselected","field_abc","field_boolean","field_date","field_derived","field_num","field_struct","file","filter","filter_small","folder","full","function_x","gear","grid","image","import","info","info-solid","info_solid_small","join","keyboard","layers","lightbulb","link","list","list_view","location","lock_locked","lock_unlocked","map","message","minus","minus_solid","more_horiz","more_vert","move","nav_charts","nav_dashboard","nav_data","nav_explore","nav_home","nav_lab","note","offline","paperclip","placeholder","plus","plus_large","plus_small","plus_solid","queued","refresh","running","save","sql","search","server","share","slack","sort_asc","sort_desc","sort","table","tag","trash","triangle_change","triangle_down","triangle_up","up-level","user","warning","warning_solid","x-large","x-small","tags","ballot","category"],p={};u.forEach((e=>{const t=l()(e).replace(/ /g,"");p[t]=t=>(0,c.tZ)(i.ZP,n()({fileName:e},t))}));const _={...d.Z,...p},g=_;var m,v;(m="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(m.register(u,"IconFileNames","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/index.tsx"),m.register(p,"iconOverrides","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/index.tsx"),m.register(_,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Icons/index.tsx")),(v="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&v(e)},737921:(e,t,r)=>{"use strict";r.d(t,{Z:()=>u});var o,s,n,a=r(205872),l=r.n(a),d=r(211965),i=(r(667294),r(582191)),c=r(751995);function u(e){const t=(0,c.Fg)(),{colors:r,transitionTiming:o}=t,{type:s,onClick:n,children:a,...u}=e,{primary:p,secondary:_,grayscale:g,success:m,warning:v,error:h,info:f}=r;let b=g.light3,E=n?p.light2:g.light3,R=n?g.light2:"transparent",y=n?p.light1:"transparent",O=g.dark1;if(s&&"default"!==s){let e;O=g.light4,e="success"===s?m:"warning"===s?v:"danger"===s?h:"info"===s?f:"secondary"===s?_:p,b=e.base,E=n?e.dark1:e.base,R=n?e.dark1:"transparent",y=n?e.dark2:"transparent"}return(0,d.tZ)(i.Vp,l()({onClick:n},u,{css:(0,d.iv)({transition:`background-color ${o}s`,whiteSpace:"nowrap",cursor:n?"pointer":"default",overflow:"hidden",textOverflow:"ellipsis",backgroundColor:b,borderColor:R,borderRadius:21,padding:"0.35em 0.8em",lineHeight:1,color:O,maxWidth:"100%","&:hover":{backgroundColor:E,borderColor:y,opacity:1}},"","")}),a)}e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),("undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e})(u,"useTheme{theme}",(()=>[c.Fg])),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&s.register(u,"Label","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Label/index.tsx"),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)},672570:(e,t,r)=>{"use strict";r.d(t,{h:()=>d,fz:()=>i,K7:()=>c,RS:()=>u,bM:()=>p,ws:()=>_,Dz:()=>g,Gb:()=>m,s2:()=>v});var o,s=r(714670),n=r.n(s),a=r(101927);function l(e){return`${e}-${n().generate()}`}e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const d="ADD_TOAST";function i({toastType:e,text:t,duration:r=8e3,noDuplicate:o=!1}){return{type:d,payload:{id:l(e),toastType:e,text:t,duration:r,noDuplicate:o}}}const c="REMOVE_TOAST";function u(e){return{type:c,payload:{id:e}}}function p(e,t){return i({text:e,toastType:a.p.INFO,duration:4e3,...t})}function _(e,t){return i({text:e,toastType:a.p.SUCCESS,duration:4e3,...t})}function g(e,t){return i({text:e,toastType:a.p.WARNING,duration:6e3,...t})}function m(e,t){return i({text:e,toastType:a.p.DANGER,duration:8e3,...t})}const v={addInfoToast:p,addSuccessToast:_,addWarningToast:g,addDangerToast:m};var h,f;(h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(h.register(l,"getToastUuid","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(d,"ADD_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(i,"addToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(c,"REMOVE_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(u,"removeToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register("ADD_INFO_TOAST","ADD_INFO_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(p,"addInfoToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register("ADD_SUCCESS_TOAST","ADD_SUCCESS_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(_,"addSuccessToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register("ADD_WARNING_TOAST","ADD_WARNING_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(g,"addWarningToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register("ADD_DANGER_TOAST","ADD_DANGER_TOAST","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(m,"addDangerToast","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts"),h.register(v,"toastActions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/actions.ts")),(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&f(e)},101927:(e,t,r)=>{"use strict";var o,s,n,a;r.d(t,{p:()=>s}),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature,function(e){e.INFO="INFO_TOAST",e.SUCCESS="SUCCESS_TOAST",e.WARNING="WARNING_TOAST",e.DANGER="DANGER_TOAST"}(s||(s={})),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&n.register(s,"ToastType","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/types.ts"),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&a(e)},414114:(e,t,r)=>{"use strict";r.d(t,{Z:()=>c,e:()=>u});var o,s=r(667294),n=r(14890),a=r(137703),l=r(672570);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e);var d="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const i={addInfoToast:l.bM,addSuccessToast:l.ws,addWarningToast:l.Dz,addDangerToast:l.Gb};function c(e){return(0,a.$j)(null,(e=>(0,n.DE)(i,e)))(e)}function u(){const e=(0,a.I0)();return(0,s.useMemo)((()=>(0,n.DE)(i,e)),[e])}var p,_;d(u,"useDispatch{dispatch}\nuseMemo{}",(()=>[a.I0])),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(p.register(i,"toasters","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/withToasts.tsx"),p.register(c,"withToasts","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/withToasts.tsx"),p.register(u,"useToasts","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/MessageToasts/withToasts.tsx")),(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&_(e)},130742:(e,t,r)=>{"use strict";r.d(t,{o:()=>y,Z:()=>P});var o,s=r(205872),n=r.n(s),a=r(414293),l=r.n(a),d=r(667294),i=r(751995),c=r(455867),u=r(211965),p=r(582191),_=r(835932),g=r(929119),m=r(861193),v=r.n(m);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e);var h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const f="380px",b="100vh",E="100vw",R=e=>(0,u.tZ)(p.u_,n()({},e,{maskTransitionName:""})),y=(0,i.iK)(R)`
  ${({theme:e,responsive:t,maxWidth:r})=>t&&(0,u.iv)("max-width:",null!=r?r:"900px",";padding-left:",3*e.gridUnit,"px;padding-right:",3*e.gridUnit,"px;","")}

  .ant-modal-header {
    background-color: ${({theme:e})=>e.colors.grayscale.light4};
    border-radius: ${({theme:e})=>e.borderRadius}px
      ${({theme:e})=>e.borderRadius}px 0 0;
    padding-left: ${({theme:e})=>4*e.gridUnit}px;
    padding-right: ${({theme:e})=>4*e.gridUnit}px;

    .ant-modal-title h4 {
      display: flex;
      margin: 0;
      align-items: center;
    }
  }

  .ant-modal-close-x {
    display: flex;
    align-items: center;

    .close {
      flex: 1 1 auto;
      margin-bottom: ${({theme:e})=>e.gridUnit}px;
      color: ${({theme:e})=>e.colors.secondary.dark1};
      font-size: 32px;
      font-weight: ${({theme:e})=>e.typography.weights.light};
    }
  }

  .ant-modal-body {
    padding: ${({theme:e})=>4*e.gridUnit}px;
    overflow: auto;
    ${({resizable:e,height:t})=>!e&&t&&`height: ${t};`}
  }
  .ant-modal-footer {
    border-top: ${({theme:e})=>e.gridUnit/4}px solid
      ${({theme:e})=>e.colors.grayscale.light2};
    padding: ${({theme:e})=>4*e.gridUnit}px;

    .btn {
      font-size: 12px;
      text-transform: uppercase;
    }

    .btn + .btn {
      margin-left: ${({theme:e})=>2*e.gridUnit}px;
    }
  }

  // styling for Tabs component
  // Aaron note 20-11-19: this seems to be exclusively here for the Edit Database modal.
  // TODO: remove this as it is a special case.
  .ant-tabs-top {
    margin-top: -${({theme:e})=>4*e.gridUnit}px;
  }

  &.no-content-padding .ant-modal-body {
    padding: 0;
  }

  ${({draggable:e,theme:t})=>e&&`\n    .ant-modal-header {\n      padding: 0;\n      .draggable-trigger {\n          cursor: move;\n          padding: ${4*t.gridUnit}px;\n          width: 100%;\n        }\n    }\n  `};

  ${({resizable:e,hideFooter:t})=>e&&`\n    .resizable {\n      pointer-events: all;\n\n      .resizable-wrapper {\n        height: 100%;\n      }\n\n      .ant-modal-content {\n        height: 100%;\n\n        .ant-modal-body {\n          /* 100% - header height - footer height */\n          height: ${t?"calc(100% - 55px);":"calc(100% - 55px - 65px);"}\n        }\n      }\n    }\n  `}
`,O=({children:e,disablePrimaryButton:t=!1,onHide:r,onHandledPrimaryAction:o,primaryButtonName:s=(0,c.t)("OK"),primaryButtonType:a="primary",show:i,name:p,title:m,width:h,maxWidth:R,responsive:O=!1,centered:T,footer:L,hideFooter:P,wrapProps:C,draggable:M=!1,resizable:x=!1,resizableConfig:A={maxHeight:b,maxWidth:E,minHeight:P?109:174,minWidth:f,enable:{bottom:!0,bottomLeft:!1,bottomRight:!0,left:!1,top:!1,topLeft:!1,topRight:!1,right:!0}},draggableConfig:N,destroyOnClose:I,...H})=>{const D=(0,d.useRef)(null),[G,S]=(0,d.useState)(),[U,k]=(0,d.useState)(!0),Z=l()(L)?[(0,u.tZ)(_.Z,{key:"back",onClick:r,cta:!0,"data-test":"modal-cancel-button"},(0,c.t)("Cancel")),(0,u.tZ)(_.Z,{key:"submit",buttonStyle:a,disabled:t,onClick:o,cta:!0,"data-test":"modal-confirm-button"},s)]:L,j=h||(O?"100vw":"600px"),w=!(x||M);return(0,u.tZ)(y,n()({centered:!!T,onOk:o,onCancel:r,width:j,maxWidth:R,responsive:O,visible:i,title:(0,u.tZ)((()=>M?(0,u.tZ)("div",{className:"draggable-trigger",onMouseOver:()=>U&&k(!1),onMouseOut:()=>!U&&k(!0)},m):(0,u.tZ)(d.Fragment,null,m)),null),closeIcon:(0,u.tZ)("span",{className:"close","aria-hidden":"true"},"×"),footer:P?null:Z,hideFooter:P,wrapProps:{"data-test":`${p||m}-modal`,...C},modalRender:e=>x||M?(0,u.tZ)(v(),n()({disabled:!M||U,bounds:G,onStart:(e,t)=>((e,t)=>{var r,o,s;const{clientWidth:n,clientHeight:a}=null==(r=window)||null==(o=r.document)?void 0:o.documentElement,l=null==D||null==(s=D.current)?void 0:s.getBoundingClientRect();l&&S({left:-(null==l?void 0:l.left)+(null==t?void 0:t.x),right:n-((null==l?void 0:l.right)-(null==t?void 0:t.x)),top:-(null==l?void 0:l.top)+(null==t?void 0:t.y),bottom:a-((null==l?void 0:l.bottom)-(null==t?void 0:t.y))})})(0,t)},N),x?(0,u.tZ)(g.e,n()({className:"resizable"},A),(0,u.tZ)("div",{className:"resizable-wrapper",ref:D},e)):(0,u.tZ)("div",{ref:D},e)):e,mask:w,draggable:M,resizable:x,destroyOnClose:I||x||M},H),e)};h(O,"useRef{draggableRef}\nuseState{[bounds, setBounds]}\nuseState{[dragDisabled, setDragDisabled](true)}"),O.displayName="Modal";const T=Object.assign(O,{error:p.u_.error,warning:p.u_.warning,confirm:p.u_.confirm,useModal:p.u_.useModal}),L=T,P=L;var C,M;(C="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(C.register(55,"MODAL_HEADER_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(54,"MODAL_MIN_CONTENT_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(65,"MODAL_FOOTER_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(109,"RESIZABLE_MIN_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(f,"RESIZABLE_MIN_WIDTH","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(b,"RESIZABLE_MAX_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(E,"RESIZABLE_MAX_WIDTH","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(R,"BaseModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(y,"StyledModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(O,"CustomModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(T,"Modal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx"),C.register(L,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Modal/Modal.tsx")),(M="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&M(e)},574520:(e,t,r)=>{"use strict";r.d(t,{o:()=>o.o,Z:()=>o.Z});var o=r(130742);"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature},367135:(e,t,r)=>{"use strict";r.d(t,{Z:()=>i}),r(667294);var o,s=r(751995),n=r(982833),a=r(211965);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const l=(0,s.iK)((({striped:e,...t})=>(0,a.tZ)(n.Z,t)))`
  line-height: 0;
  position: static;
  .ant-progress-inner {
    position: static;
  }
  .ant-progress-outer {
    ${({percent:e})=>!e&&"display: none;"}
  }
  .ant-progress-text {
    font-size: ${({theme:e})=>e.typography.sizes.s}px;
  }
  .ant-progress-bg {
    position: static;
    ${({striped:e})=>e&&"\n        background-image: linear-gradient(45deg,\n            rgba(255, 255, 255, 0.15) 25%,\n            transparent 25%, transparent 50%,\n            rgba(255, 255, 255, 0.15) 50%,\n            rgba(255, 255, 255, 0.15) 75%,\n            transparent 75%, transparent) !important;\n        background-size: 1rem 1rem !important;\n        "};
  }
`,d=l,i=d;var c,u;(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(c.register(l,"ProgressBar","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ProgressBar/index.tsx"),c.register(d,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ProgressBar/index.tsx")),(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&u(e)},358593:(e,t,r)=>{"use strict";r.d(t,{u:()=>u});var o,s=r(205872),n=r.n(s),a=r(667294),l=r(751995),d=r(211965),i=r(931097);e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e);var c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const u=e=>{const t=(0,l.Fg)();return(0,d.tZ)(a.Fragment,null,(0,d.tZ)(d.xB,{styles:d.iv`
          .ant-tooltip-open {
            display: inline-block;
            &::after {
              content: '';
              display: block;
            }
          }
        `}),(0,d.tZ)(i.Z,n()({overlayStyle:{fontSize:t.typography.sizes.s,lineHeight:"1.6"},color:`${t.colors.grayscale.dark2}e6`},e)))};var p,_;c(u,"useTheme{theme}",(()=>[l.Fg])),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&p.register(u,"Tooltip","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/Tooltip/index.tsx"),(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&_(e)},710222:(e,t,r)=>{"use strict";var o;r.d(t,{Z:()=>a}),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const s=async e=>new Promise(((t,r)=>{const o=document.getSelection();if(o){o.removeAllRanges();const t=document.createRange(),s=document.createElement("span");s.textContent=e,s.style.position="fixed",s.style.top="0",s.style.clip="rect(0, 0, 0, 0)",s.style.whiteSpace="pre",document.body.appendChild(s),t.selectNode(s),o.addRange(t);try{document.execCommand("copy")||r()}catch(e){r()}document.body.removeChild(s),o.removeRange?o.removeRange(t):o.removeAllRanges()}t()})),n=s,a=n;var l,d;(l="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(l.register(s,"copyTextToClipboard","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/copy.ts"),l.register(n,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/copy.ts")),(d="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&d(e)},966785:(e,t,r)=>{"use strict";var o;r.d(t,{Z:()=>a}),e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const s={SESSION_TIMED_OUT:"Your session timed out, please refresh your page and try again."},n=s,a=n;var l,d;(l="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(l.register(s,"COMMON_ERR_MESSAGES","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/errorMessages.ts"),l.register(n,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/errorMessages.ts")),(d="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&d(e)},998286:(e,t,r)=>{"use strict";r.d(t,{M:()=>i,O:()=>c});var o,s,n,a=r(455867),l=r(167663),d=r(966785);function i(e){let t={...e};var r,o;return t.errors&&t.errors.length>0&&(t.error=t.description=t.errors[0].message,t.link=null==(r=t.errors[0])||null==(o=r.extra)?void 0:o.link),t.stack?t={...t,error:(0,a.t)("Unexpected error: ")+(t.description||(0,a.t)("(no description, click to see stack trace)")),stacktrace:t.stack}:t.responseText&&t.responseText.indexOf("CSRF")>=0&&(t={...t,error:(0,a.t)(d.Z.SESSION_TIMED_OUT)}),{...t,error:t.error}}function c(e){return new Promise((t=>{if("string"==typeof e)t({error:e});else{const r=e instanceof Response?e:e.response;if(r&&!r.bodyUsed)r.clone().json().then((e=>{const o={...r,...e};t(i(o))})).catch((()=>{r.text().then((e=>{t({...r,error:e})}))}));else if("statusText"in e&&"timeout"===e.statusText&&"timeout"in e)t({...r,error:"Request timed out",errors:[{error_type:l.C.FRONTEND_TIMEOUT_ERROR,extra:{timeout:e.timeout/1e3,issue_codes:[{code:1e3,message:(0,a.t)("Issue 1000 - The dataset is too large to query.")},{code:1001,message:(0,a.t)("Issue 1001 - The database is under an unusual load.")}]},level:"error",message:"Request timed out"}]});else{let o=e.statusText||e.message;o||(console.error("non-standard error:",e),o=(0,a.t)("An error occurred")),t({...r,error:o})}}}))}e=r.hmd(e),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&o(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature,(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(s.register(i,"parseErrorJson","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/getClientErrorObject.ts"),s.register(c,"getClientErrorObject","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/utils/getClientErrorObject.ts")),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)},335782:(e,t,r)=>{var o={"./alert.svg":[857249,7249],"./alert_solid.svg":[752797,2797],"./alert_solid_small.svg":[71256,1256],"./ballot.svg":[587760,7760],"./binoculars.svg":[738970,8970],"./bolt.svg":[304794,4794],"./bolt_small.svg":[49510,9510],"./bolt_small_run.svg":[336883,6883],"./calendar.svg":[265816,5816],"./cancel-x.svg":[577654,7654],"./cancel.svg":[114757,4757],"./cancel_solid.svg":[755777,5777],"./card_view.svg":[25838,5838],"./cards.svg":[581293,1293],"./cards_locked.svg":[369052,9052],"./caret_down.svg":[187832,7832],"./caret_left.svg":[180310,310],"./caret_right.svg":[164817,4817],"./caret_up.svg":[639811,9811],"./category.svg":[824851,4851],"./certified.svg":[88695,8695],"./check.svg":[983544,3544],"./checkbox-half.svg":[457405,7405],"./checkbox-off.svg":[475281,5281],"./checkbox-on.svg":[99013,9013],"./circle.svg":[160183,183],"./circle_check.svg":[193558,3558],"./circle_check_solid.svg":[570992,992],"./clock.svg":[350597,597],"./close.svg":[750999,999],"./code.svg":[916981,6981],"./cog.svg":[45962,5962],"./collapse.svg":[424266,4266],"./color_palette.svg":[265580,5580],"./components.svg":[80312,312],"./copy.svg":[923141,3141],"./cross-filter-badge.svg":[664625,4625],"./cursor_target.svg":[896758,6758],"./database.svg":[815249,5249],"./dataset_physical.svg":[308312,8312],"./dataset_virtual.svg":[365330,5330],"./dataset_virtual_greyscale.svg":[84810,4810],"./default_db_image.svg":[551398,1398],"./download.svg":[900112,112],"./drag.svg":[886507,6507],"./edit.svg":[793871,3871],"./edit_alt.svg":[986167,6167],"./email.svg":[450504,6668],"./error.svg":[467584,7584],"./error_solid.svg":[525641,5641],"./error_solid_small.svg":[692561,2983],"./error_solid_small_red.svg":[504273,4273],"./exclamation.svg":[235771,5771],"./expand.svg":[147922,7922],"./eye.svg":[911493,1493],"./eye_slash.svg":[239109,9109],"./favorite-selected.svg":[151568,1568],"./favorite-unselected.svg":[986682,6682],"./favorite_small_selected.svg":[801351,1351],"./field_abc.svg":[470215,215],"./field_boolean.svg":[687405,5507],"./field_date.svg":[165226,5226],"./field_derived.svg":[644732,4732],"./field_num.svg":[235201,5201],"./field_struct.svg":[391899,1899],"./file.svg":[620057,57],"./filter.svg":[519305,9305],"./filter_small.svg":[954474,4474],"./folder.svg":[686420,6420],"./full.svg":[923985,3985],"./function_x.svg":[244662,4662],"./gear.svg":[107610,7610],"./grid.svg":[68425,8425],"./image.svg":[692264,2264],"./import.svg":[142698,2698],"./info-solid.svg":[871605,1605],"./info.svg":[2713,2713],"./info_solid_small.svg":[733606,3606],"./join.svg":[985998,5998],"./keyboard.svg":[587850,7850],"./layers.svg":[785832,5832],"./lightbulb.svg":[854797,4797],"./link.svg":[899558,9558],"./list.svg":[845707,5707],"./list_view.svg":[938682,8682],"./location.svg":[361174,1174],"./lock_locked.svg":[155359,5359],"./lock_unlocked.svg":[906207,6207],"./map.svg":[18463,8463],"./message.svg":[664458,4458],"./minus.svg":[697183,7183],"./minus_solid.svg":[706371,6371],"./more_horiz.svg":[339325,9325],"./more_vert.svg":[991185,1185],"./move.svg":[74139,4139],"./nav_charts.svg":[275350,5350],"./nav_dashboard.svg":[666303,6303],"./nav_data.svg":[402267,2267],"./nav_explore.svg":[983749,3749],"./nav_home.svg":[844667,4667],"./nav_lab.svg":[743567,3567],"./note.svg":[246597,6126],"./offline.svg":[153265,3265],"./paperclip.svg":[522079,2079],"./placeholder.svg":[318349,8349],"./plus.svg":[817460,7460],"./plus_large.svg":[566150,6150],"./plus_small.svg":[396447,6447],"./plus_solid.svg":[470600,600],"./queued.svg":[963240,3240],"./refresh.svg":[425367,5367],"./running.svg":[505224,1005],"./save.svg":[136254,6254],"./search.svg":[230177,177],"./server.svg":[811075,1075],"./share.svg":[311263,1263],"./slack.svg":[342439,2439],"./sort.svg":[520336,336],"./sort_asc.svg":[579393,9393],"./sort_desc.svg":[732646,2646],"./sql.svg":[113325,3325],"./table.svg":[772403,2403],"./tag.svg":[530158,158],"./tags.svg":[890363,363],"./transparent.svg":[487803,7803],"./trash.svg":[362105,2105],"./triangle_change.svg":[498398,8398],"./triangle_down.svg":[240826,826],"./triangle_up.svg":[936819,6819],"./up-level.svg":[165972,5972],"./user.svg":[899767,9767],"./warning.svg":[404758,4758],"./warning_solid.svg":[275224,5224],"./x-large.svg":[863955,3955],"./x-small.svg":[107716,7716]};function s(e){if(!r.o(o,e))return Promise.resolve().then((()=>{var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=o[e],s=t[0];return r.e(t[1]).then((()=>r(s)))}s.keys=()=>Object.keys(o),s.id=335782,e.exports=s}}]);