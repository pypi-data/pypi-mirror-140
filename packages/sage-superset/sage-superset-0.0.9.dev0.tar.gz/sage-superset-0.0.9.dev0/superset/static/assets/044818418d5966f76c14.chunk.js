"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[4502],{789719:(e,t,a)=>{a.d(t,{Z:()=>_});var s=a(667294),r=a(751995),o=a(835932),n=a(87693);function l(){return l=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var a=arguments[t];for(var s in a)Object.prototype.hasOwnProperty.call(a,s)&&(e[s]=a[s])}return e},l.apply(this,arguments)}const i={position:"absolute",bottom:0,left:0,height:0,overflow:"hidden","padding-top":0,"padding-bottom":0,border:"none"},d=["box-sizing","width","font-size","font-weight","font-family","font-style","letter-spacing","text-indent","white-space","word-break","overflow-wrap","padding-left","padding-right"];function c(e,t){for(;e&&t--;)e=e.previousElementSibling;return e}const u={basedOn:void 0,className:"",component:"div",ellipsis:"…",maxLine:1,onReflow(){},text:"",trimRight:!0,winWidth:void 0},p=Object.keys(u);class m extends s.Component{constructor(e){super(e),this.state={text:e.text,clamped:!1},this.units=[],this.maxLine=0,this.canvas=null}componentDidMount(){this.initCanvas(),this.reflow(this.props)}componentDidUpdate(e){e.winWidth!==this.props.winWidth&&this.copyStyleToCanvas(),this.props!==e&&this.reflow(this.props)}componentWillUnmount(){this.canvas.parentNode.removeChild(this.canvas)}setState(e,t){return void 0!==e.clamped&&(this.clamped=e.clamped),super.setState(e,t)}initCanvas(){if(this.canvas)return;const e=this.canvas=document.createElement("div");e.className=`LinesEllipsis-canvas ${this.props.className}`,e.setAttribute("aria-hidden","true"),this.copyStyleToCanvas(),Object.keys(i).forEach((t=>{e.style[t]=i[t]})),document.body.appendChild(e)}copyStyleToCanvas(){const e=window.getComputedStyle(this.target);d.forEach((t=>{this.canvas.style[t]=e[t]}))}reflow(e){const t=e.basedOn||(/^[\x00-\x7F]+$/.test(e.text)?"words":"letters");switch(t){case"words":this.units=e.text.split(/\b|(?=\W)/);break;case"letters":this.units=Array.from(e.text);break;default:throw new Error(`Unsupported options basedOn: ${t}`)}this.maxLine=+e.maxLine||1,this.canvas.innerHTML=this.units.map((e=>`<span class='LinesEllipsis-unit'>${e}</span>`)).join("");const a=this.putEllipsis(this.calcIndexes()),s=a>-1,r={clamped:s,text:s?this.units.slice(0,a).join(""):e.text};this.setState(r,e.onReflow.bind(this,r))}calcIndexes(){const e=[0];let t=this.canvas.firstElementChild;if(!t)return e;let a=0,s=1,r=t.offsetTop;for(;(t=t.nextElementSibling)&&(t.offsetTop>r&&(s++,e.push(a),r=t.offsetTop),a++,!(s>this.maxLine)););return e}putEllipsis(e){if(e.length<=this.maxLine)return-1;const t=e[this.maxLine],a=this.units.slice(0,t),s=this.canvas.children[t].offsetTop;this.canvas.innerHTML=a.map(((e,t)=>`<span class='LinesEllipsis-unit'>${e}</span>`)).join("")+`<wbr><span class='LinesEllipsis-ellipsis'>${this.props.ellipsis}</span>`;const r=this.canvas.lastElementChild;let o=c(r,2);for(;o&&(r.offsetTop>s||r.offsetHeight>o.offsetHeight||r.offsetTop>o.offsetTop);)this.canvas.removeChild(o),o=c(r,2),a.pop();return a.length}isClamped(){return this.clamped}render(){const{text:e,clamped:t}=this.state,a=this.props,{component:r,ellipsis:o,trimRight:n,className:i}=a,d=function(e,t){if(null==e)return{};var a,s,r={},o=Object.keys(e);for(s=0;s<o.length;s++)a=o[s],t.indexOf(a)>=0||(r[a]=e[a]);return r}(a,["component","ellipsis","trimRight","className"]);return s.createElement(r,l({className:`LinesEllipsis ${t?"LinesEllipsis--clamped":""} ${i}`,ref:e=>this.target=e},function(e,t){if(!e||"object"!=typeof e)return e;const a={};return Object.keys(e).forEach((s=>{t.indexOf(s)>-1||(a[s]=e[s])})),a}(d,p)),t&&n?e.replace(/[\s\uFEFF\xA0]+$/,""):e,s.createElement("wbr",null),t&&s.createElement("span",{className:"LinesEllipsis-ellipsis"},o))}}m.defaultProps=u;const h=m;var g,b=a(211965);e=a.hmd(e),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&g(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const v=(0,r.iK)(o.Z)`
  height: auto;
  display: flex;
  flex-direction: column;
  padding: 0;
`,f=r.iK.div`
  padding: ${({theme:e})=>4*e.gridUnit}px;
  height: ${({theme:e})=>18*e.gridUnit}px;
  margin: ${({theme:e})=>3*e.gridUnit}px 0;

  .default-db-icon {
    font-size: 36px;
    color: ${({theme:e})=>e.colors.grayscale.base};
    margin-right: 0;
    span:first-of-type {
      margin-right: 0;
    }
  }

  &:first-of-type {
    margin-right: 0;
  }

  img {
    width: ${({theme:e})=>10*e.gridUnit}px;
    height: ${({theme:e})=>10*e.gridUnit}px;
    margin: 0;
    &:first-of-type {
      margin-right: 0;
    }
  }
  svg {
    &:first-of-type {
      margin-right: 0;
    }
  }
`,y=r.iK.div`
  max-height: calc(1.5em * 2);
  white-space: break-spaces;

  &:first-of-type {
    margin-right: 0;
  }

  .LinesEllipsis {
    &:first-of-type {
      margin-right: 0;
    }
  }
`,x=r.iK.div`
  padding: ${({theme:e})=>4*e.gridUnit}px 0;
  border-radius: 0 0 ${({theme:e})=>e.borderRadius}px
    ${({theme:e})=>e.borderRadius}px;
  background-color: ${({theme:e})=>e.colors.grayscale.light4};
  width: 100%;
  line-height: 1.5em;
  overflow: hidden;
  white-space: no-wrap;
  text-overflow: ellipsis;

  &:first-of-type {
    margin-right: 0;
  }
`,C=(0,r.iK)((({icon:e,altText:t,buttonText:a,...s})=>(0,b.tZ)(v,s,(0,b.tZ)(f,null,e&&(0,b.tZ)("img",{src:e,alt:t}),!e&&(0,b.tZ)(n.Z.DatabaseOutlined,{className:"default-db-icon","aria-label":"default-icon"})),(0,b.tZ)(x,null,(0,b.tZ)(y,null,(0,b.tZ)(h,{text:a,maxLine:"2",basedOn:"words",trimRight:!0}))))))`
  text-transform: none;
  background-color: ${({theme:e})=>e.colors.grayscale.light5};
  font-weight: ${({theme:e})=>e.typography.weights.normal};
  color: ${({theme:e})=>e.colors.grayscale.dark2};
  border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
  margin: 0;
  width: 100%;

  &:hover,
  &:focus {
    background-color: ${({theme:e})=>e.colors.grayscale.light5};
    color: ${({theme:e})=>e.colors.grayscale.dark2};
    border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    box-shadow: 4px 4px 20px ${({theme:e})=>e.colors.grayscale.light2};
  }
`,Z=C,_=Z;var w,D;(w="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(w.register(v,"StyledButton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx"),w.register(f,"StyledImage","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx"),w.register(y,"StyledInner","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx"),w.register(x,"StyledBottom","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx"),w.register(C,"IconButton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx"),w.register(Z,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IconButton/index.tsx")),(D="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&D(e)},727989:(e,t,a)=>{a.d(t,{Z:()=>v});var s,r=a(667294),o=a(751995),n=a(455867),l=a(835932),i=a(574520),d=a(582191),c=a(34858),u=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const m=o.iK.div`
  display: block;
  color: ${({theme:e})=>e.colors.grayscale.base};
  font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
`,h=o.iK.div`
  padding-bottom: ${({theme:e})=>2*e.gridUnit}px;
  padding-top: ${({theme:e})=>2*e.gridUnit}px;

  & > div {
    margin: ${({theme:e})=>e.gridUnit}px 0;
  }

  &.extra-container {
    padding-top: 8px;
  }

  .confirm-overwrite {
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }

  .input-container {
    display: flex;
    align-items: center;

    label {
      display: flex;
      margin-right: ${({theme:e})=>2*e.gridUnit}px;
    }

    i {
      margin: 0 ${({theme:e})=>e.gridUnit}px;
    }
  }

  input,
  textarea {
    flex: 1 1 auto;
  }

  textarea {
    height: 160px;
    resize: none;
  }

  input::placeholder,
  textarea::placeholder {
    color: ${({theme:e})=>e.colors.grayscale.light1};
  }

  textarea,
  input[type='text'],
  input[type='number'] {
    padding: ${({theme:e})=>1.5*e.gridUnit}px
      ${({theme:e})=>2*e.gridUnit}px;
    border-style: none;
    border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    border-radius: ${({theme:e})=>e.gridUnit}px;

    &[name='name'] {
      flex: 0 1 auto;
      width: 40%;
    }

    &[name='sqlalchemy_uri'] {
      margin-right: ${({theme:e})=>3*e.gridUnit}px;
    }
  }
`,g=({resourceName:e,resourceLabel:t,passwordsNeededMessage:a,confirmOverwriteMessage:s,addDangerToast:o,onModelImport:p,show:g,onHide:b,passwordFields:v=[],setPasswordFields:f=(()=>{})})=>{const[y,x]=(0,r.useState)(!0),[C,Z]=(0,r.useState)({}),[_,w]=(0,r.useState)(!1),[D,P]=(0,r.useState)(!1),[U,S]=(0,r.useState)([]),[L,M]=(0,r.useState)(!1),E=()=>{S([]),f([]),Z({}),w(!1),P(!1),M(!1)},{state:{alreadyExists:N,passwordsNeeded:R},importResource:H}=(0,c.PW)(e,t,(e=>{E(),o(e)}));(0,r.useEffect)((()=>{f(R),R.length>0&&M(!1)}),[R,f]),(0,r.useEffect)((()=>{w(N.length>0),N.length>0&&M(!1)}),[N,w]);return y&&g&&x(!1),(0,u.tZ)(i.Z,{name:"model",className:"import-model-modal",disablePrimaryButton:0===U.length||_&&!D||L,onHandledPrimaryAction:()=>{var e;(null==(e=U[0])?void 0:e.originFileObj)instanceof File&&(M(!0),H(U[0].originFileObj,C,D).then((e=>{e&&(E(),p())})))},onHide:()=>{x(!0),b(),E()},primaryButtonName:_?(0,n.t)("Overwrite"):(0,n.t)("Import"),primaryButtonType:_?"danger":"primary",width:"750px",show:g,title:(0,u.tZ)("h4",null,(0,n.t)("Import %s",t))},(0,u.tZ)(h,null,(0,u.tZ)(d.gq,{name:"modelFile",id:"modelFile","data-test":"model-file-input",accept:".yaml,.json,.yml,.zip",fileList:U,onChange:e=>{S([{...e.file,status:"done"}])},onRemove:e=>(S(U.filter((t=>t.uid!==e.uid))),!1),customRequest:()=>{}},(0,u.tZ)(l.Z,{loading:L},"Select file"))),0===v.length?null:(0,u.tZ)(r.Fragment,null,(0,u.tZ)("h5",null,"Database passwords"),(0,u.tZ)(m,null,a),v.map((e=>(0,u.tZ)(h,{key:`password-for-${e}`},(0,u.tZ)("div",{className:"control-label"},e,(0,u.tZ)("span",{className:"required"},"*")),(0,u.tZ)("input",{name:`password-${e}`,autoComplete:`password-${e}`,type:"password",value:C[e],onChange:t=>Z({...C,[e]:t.target.value})}))))),_?(0,u.tZ)(r.Fragment,null,(0,u.tZ)(h,null,(0,u.tZ)("div",{className:"confirm-overwrite"},s),(0,u.tZ)("div",{className:"control-label"},(0,n.t)('Type "%s" to confirm',(0,n.t)("OVERWRITE"))),(0,u.tZ)("input",{"data-test":"overwrite-modal-input",id:"overwrite",type:"text",onChange:e=>{var t,a;const s=null!=(t=null==(a=e.currentTarget)?void 0:a.value)?t:"";P(s.toUpperCase()===(0,n.t)("OVERWRITE"))}}))):null)};p(g,"useState{[isHidden, setIsHidden](true)}\nuseState{[passwords, setPasswords]({})}\nuseState{[needsOverwriteConfirm, setNeedsOverwriteConfirm](false)}\nuseState{[confirmedOverwrite, setConfirmedOverwrite](false)}\nuseState{[fileList, setFileList]([])}\nuseState{[importingModel, setImportingModel](false)}\nuseImportResource{{ state: { alreadyExists, passwordsNeeded }, importResource, }}\nuseEffect{}\nuseEffect{}",(()=>[c.PW]));const b=g,v=b;var f,y;(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(f.register(m,"HelperMessage","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(h,"StyledInputContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(g,"ImportModelsModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(b,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx")),(y="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&y(e)},495413:(e,t,a)=>{a.d(t,{Y:()=>o});var s,r=a(455867);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const o={name:(0,r.t)("Data"),tabs:[{name:"Databases",label:(0,r.t)("Databases"),url:"/databaseview/list/",usesRouter:!0},{name:"Datasets",label:(0,r.t)("Datasets"),url:"/tablemodelview/list/",usesRouter:!0},{name:"Saved queries",label:(0,r.t)("Saved queries"),url:"/savedqueryview/list/",usesRouter:!0},{name:"Query history",label:(0,r.t)("Query history"),url:"/superset/sqllab/history/",usesRouter:!0}]};var n,l;(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&n.register(o,"commonMenuData","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/common.ts"),(l="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&l(e)},430075:(e,t,a)=>{a.r(t),a.d(t,{default:()=>N});var s,r=a(455867),o=a(751995),n=a(431069),l=a(667294),i=a(838703),d=a(591877),c=a(34858),u=a(440768),p=a(414114),m=a(620755),h=a(217198),g=a(358593),b=a(87693),v=a(550859),f=a(495413),y=a(727989),x=a(232228),C=a(603506),Z=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e);var _="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const w=(0,r.t)('The passwords for the databases below are needed in order to import them. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in export files, and should be added manually after the import if they are needed.'),D=(0,r.t)("You are importing one or more databases that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?"),P=(0,o.iK)(b.Z.Check)`
  color: ${({theme:e})=>e.colors.grayscale.dark1};
`,U=(0,o.iK)(b.Z.CancelX)`
  color: ${({theme:e})=>e.colors.grayscale.dark1};
`,S=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.base};
`;function L({value:e}){return e?(0,Z.tZ)(P,null):(0,Z.tZ)(U,null)}function M({addDangerToast:e,addSuccessToast:t}){const{state:{loading:a,resourceCount:s,resourceCollection:o},hasPerm:p,fetchData:_,refreshData:P}=(0,c.Yi)("database",(0,r.t)("database"),e),[U,M]=(0,l.useState)(!1),[E,N]=(0,l.useState)(null),[R,H]=(0,l.useState)(null),[j,$]=(0,l.useState)(!1),[T,A]=(0,l.useState)([]),[k,O]=(0,l.useState)(!1);function G({database:e=null,modalOpen:t=!1}={}){H(e),M(t)}const I=p("can_write"),F=p("can_write"),q=p("can_write"),z=p("can_export")&&(0,d.cr)(d.TT.VERSIONED_EXPORT),B={activeChild:"Databases",...f.Y};I&&(B.buttons=[{"data-test":"btn-create-database",name:(0,Z.tZ)(l.Fragment,null,(0,Z.tZ)("i",{className:"fa fa-plus"})," ",(0,r.t)("Database")," "),buttonStyle:"primary",onClick:()=>{G({modalOpen:!0})}}],(0,d.cr)(d.TT.VERSIONED_EXPORT)&&B.buttons.push({name:(0,Z.tZ)(g.u,{id:"import-tooltip",title:(0,r.t)("Import databases"),placement:"bottomRight"},(0,Z.tZ)(b.Z.Import,{"data-test":"import-button"})),buttonStyle:"link",onClick:()=>{$(!0)}}));const Q=(0,l.useMemo)((()=>[{accessor:"database_name",Header:(0,r.t)("Database")},{accessor:"backend",Header:(0,r.t)("Backend"),size:"lg",disableSortBy:!0},{accessor:"allow_run_async",Header:(0,Z.tZ)(g.u,{id:"allow-run-async-header-tooltip",title:(0,r.t)("Asynchronous query execution"),placement:"top"},(0,Z.tZ)("span",null,(0,r.t)("AQE"))),Cell:({row:{original:{allow_run_async:e}}})=>(0,Z.tZ)(L,{value:e}),size:"sm"},{accessor:"allow_dml",Header:(0,Z.tZ)(g.u,{id:"allow-dml-header-tooltip",title:(0,r.t)("Allow data manipulation language"),placement:"top"},(0,Z.tZ)("span",null,(0,r.t)("DML"))),Cell:({row:{original:{allow_dml:e}}})=>(0,Z.tZ)(L,{value:e}),size:"sm"},{accessor:"allow_file_upload",Header:(0,r.t)("CSV upload"),Cell:({row:{original:{allow_file_upload:e}}})=>(0,Z.tZ)(L,{value:e}),size:"md"},{accessor:"expose_in_sqllab",Header:(0,r.t)("Expose in SQL Lab"),Cell:({row:{original:{expose_in_sqllab:e}}})=>(0,Z.tZ)(L,{value:e}),size:"md"},{accessor:"created_by",disableSortBy:!0,Header:(0,r.t)("Created by"),Cell:({row:{original:{created_by:e}}})=>e?`${e.first_name} ${e.last_name}`:"",size:"xl"},{Cell:({row:{original:{changed_on_delta_humanized:e}}})=>e,Header:(0,r.t)("Last modified"),accessor:"changed_on_delta_humanized",size:"xl"},{Cell:({row:{original:e}})=>F||q||z?(0,Z.tZ)(S,{className:"actions"},q&&(0,Z.tZ)("span",{role:"button",tabIndex:0,className:"action-button","data-test":"database-delete",onClick:()=>{return t=e,n.Z.get({endpoint:`/api/v1/database/${t.id}/related_objects/`}).then((({json:e={}})=>{N({...t,chart_count:e.charts.count,dashboard_count:e.dashboards.count,sqllab_tab_count:e.sqllab_tab_states.count})})).catch((0,u.v$)((e=>(0,r.t)("An error occurred while fetching database related data: %s",e))));var t}},(0,Z.tZ)(g.u,{id:"delete-action-tooltip",title:(0,r.t)("Delete database"),placement:"bottom"},(0,Z.tZ)(b.Z.Trash,null))),z&&(0,Z.tZ)(g.u,{id:"export-action-tooltip",title:(0,r.t)("Export"),placement:"bottom"},(0,Z.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>{var t;void 0!==(t=e).id&&((0,x.Z)("database",[t.id],(()=>{O(!1)})),O(!0))}},(0,Z.tZ)(b.Z.Share,null))),F&&(0,Z.tZ)(g.u,{id:"edit-action-tooltip",title:(0,r.t)("Edit"),placement:"bottom"},(0,Z.tZ)("span",{role:"button","data-test":"database-edit",tabIndex:0,className:"action-button",onClick:()=>G({database:e,modalOpen:!0})},(0,Z.tZ)(b.Z.EditAlt,{"data-test":"edit-alt"})))):null,Header:(0,r.t)("Actions"),id:"actions",hidden:!F&&!q,disableSortBy:!0}]),[q,F,z]),V=(0,l.useMemo)((()=>[{Header:(0,r.t)("Expose in SQL Lab"),id:"expose_in_sqllab",input:"select",operator:v.p.equals,unfilteredLabel:"All",selects:[{label:"Yes",value:!0},{label:"No",value:!1}]},{Header:(0,Z.tZ)(g.u,{id:"allow-run-async-filter-header-tooltip",title:(0,r.t)("Asynchronous query execution"),placement:"top"},(0,Z.tZ)("span",null,(0,r.t)("AQE"))),id:"allow_run_async",input:"select",operator:v.p.equals,unfilteredLabel:"All",selects:[{label:"Yes",value:!0},{label:"No",value:!1}]},{Header:(0,r.t)("Search"),id:"database_name",input:"search",operator:v.p.contains}]),[]);return(0,Z.tZ)(l.Fragment,null,(0,Z.tZ)(m.Z,B),(0,Z.tZ)(C.Z,{databaseId:null==R?void 0:R.id,show:U,onHide:G,onDatabaseAdd:()=>{P()}}),E&&(0,Z.tZ)(h.Z,{description:(0,r.t)("The database %s is linked to %s charts that appear on %s dashboards and users have %s SQL Lab tabs using this database open. Are you sure you want to continue? Deleting the database will break those objects.",E.database_name,E.chart_count,E.dashboard_count,E.sqllab_tab_count),onConfirm:()=>{E&&function({id:a,database_name:s}){n.Z.delete({endpoint:`/api/v1/database/${a}`}).then((()=>{P(),t((0,r.t)("Deleted: %s",s)),N(null)}),(0,u.v$)((t=>e((0,r.t)("There was an issue deleting %s: %s",s,t)))))}(E)},onHide:()=>N(null),open:!0,title:(0,r.t)("Delete Database?")}),(0,Z.tZ)(v.Z,{className:"database-list-view",columns:Q,count:s,data:o,fetchData:_,filters:V,initialSort:[{id:"changed_on_delta_humanized",desc:!0}],loading:a,pageSize:25}),(0,Z.tZ)(y.Z,{resourceName:"database",resourceLabel:(0,r.t)("database"),passwordsNeededMessage:w,confirmOverwriteMessage:D,addDangerToast:e,addSuccessToast:t,onModelImport:()=>{$(!1),P(),t((0,r.t)("Database imported"))},show:j,onHide:()=>{$(!1)},passwordFields:T,setPasswordFields:A}),k&&(0,Z.tZ)(i.Z,null))}_(M,"useListViewResource{{ state: { loading, resourceCount: databaseCount, resourceCollection: databases, }, hasPerm, fetchData, refreshData, }}\nuseState{[databaseModalOpen, setDatabaseModalOpen](false)}\nuseState{[databaseCurrentlyDeleting, setDatabaseCurrentlyDeleting](null)}\nuseState{[currentDatabase, setCurrentDatabase](null)}\nuseState{[importingDatabase, showImportModal](false)}\nuseState{[passwordFields, setPasswordFields]([])}\nuseState{[preparingExport, setPreparingExport](false)}\nuseMemo{columns}\nuseMemo{filters}",(()=>[c.Yi]));const E=(0,p.Z)(M),N=E;var R,H;(R="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(R.register(25,"PAGE_SIZE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(w,"PASSWORDS_NEEDED_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(D,"CONFIRM_OVERWRITE_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(P,"IconCheck","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(U,"IconCancelX","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(S,"Actions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(L,"BooleanDisplay","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(M,"DatabaseList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx"),R.register(E,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseList.tsx")),(H="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&H(e)},523419:(e,t,a)=>{a.d(t,{FQ:()=>u,xP:()=>p,WT:()=>m,qm:()=>h,Uy:()=>g,w_:()=>b,Wj:()=>v,mB:()=>f});var s,r=a(667294),o=a(455867),n=a(582191),l=a(608272),i=a(187858),d=a(853199),c=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const u=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r})=>{var n;return(0,c.tZ)(i.Z,{id:"host",name:"host",value:null==r||null==(n=r.parameters)?void 0:n.host,required:e,hasTooltip:!0,tooltipText:(0,o.t)("This can be either an IP address (e.g. 127.0.0.1) or a domain name (e.g. mydatabase.com)."),validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.host,placeholder:(0,o.t)("e.g. 127.0.0.1"),className:"form-group-w-50",label:(0,o.t)("Host"),onChange:t.onParametersChange})},p=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:n})=>{var l;return(0,c.tZ)(r.Fragment,null,(0,c.tZ)(i.Z,{id:"port",name:"port",type:"number",required:e,value:null==n||null==(l=n.parameters)?void 0:l.port,validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.port,placeholder:(0,o.t)("e.g. 5432"),className:"form-group-w-50",label:"Port",onChange:t.onParametersChange}))},m=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r})=>{var n;return(0,c.tZ)(i.Z,{id:"database",name:"database",required:e,value:null==r||null==(n=r.parameters)?void 0:n.database,validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.database,placeholder:(0,o.t)("e.g. world_population"),label:(0,o.t)("Database name"),onChange:t.onParametersChange,helpText:(0,o.t)("Copy the name of the  database you are trying to connect to.")})},h=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r})=>{var n;return(0,c.tZ)(i.Z,{id:"username",name:"username",required:e,value:null==r||null==(n=r.parameters)?void 0:n.username,validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.username,placeholder:(0,o.t)("e.g. Analytics"),label:(0,o.t)("Username"),onChange:t.onParametersChange})},g=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r,isEditMode:n})=>{var l;return(0,c.tZ)(i.Z,{id:"password",name:"password",required:e,type:n&&"password",value:null==r||null==(l=r.parameters)?void 0:l.password,validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.password,placeholder:(0,o.t)("e.g. ********"),label:(0,o.t)("Password"),onChange:t.onParametersChange})},b=({changeMethods:e,getValidation:t,validationErrors:a,db:s})=>(0,c.tZ)(r.Fragment,null,(0,c.tZ)(i.Z,{id:"database_name",name:"database_name",required:!0,value:null==s?void 0:s.database_name,validationMethods:{onBlur:t},errorMessage:null==a?void 0:a.database_name,placeholder:"",label:(0,o.t)("Display Name"),onChange:e.onChange,helpText:(0,o.t)("Pick a nickname for this database to display as in Superset.")})),v=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r})=>(0,c.tZ)(i.Z,{id:"query_input",name:"query_input",required:e,value:(null==r?void 0:r.query_input)||"",validationMethods:{onBlur:a},errorMessage:null==s?void 0:s.query,placeholder:(0,o.t)("e.g. param1=value1&param2=value2"),label:(0,o.t)("Additional Parameters"),onChange:t.onQueryChange,helpText:(0,o.t)("Add additional custom parameters")}),f=({isEditMode:e,changeMethods:t,db:a,sslForced:s})=>{var r;return(0,c.tZ)("div",{css:e=>(0,d.bC)(e)},(0,c.tZ)(n.rs,{disabled:s&&!e,checked:(null==a||null==(r=a.parameters)?void 0:r.encryption)||s,onChange:e=>{t.onParametersChange({target:{type:"toggle",name:"encryption",checked:!0,value:e}})}}),(0,c.tZ)("span",{css:d.ob},"SSL"),(0,c.tZ)(l.Z,{tooltip:(0,o.t)('SSL Mode "require" will be used.'),placement:"right",viewBox:"0 -5 24 24"}))};var y,x;(y="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(y.register(u,"hostField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(p,"portField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(m,"databaseField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(h,"usernameField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(g,"passwordField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(b,"displayField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(v,"queryField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx"),y.register(f,"forceSSLField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/CommonParameters.tsx")),(x="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&x(e)},709419:(e,t,a)=>{a.d(t,{N:()=>x});var s=a(667294),r=a(455867),o=a(582191),n=a(608272),l=a(902857);const i={icon:{tag:"svg",attrs:{viewBox:"64 64 896 896",focusable:"false"},children:[{tag:"path",attrs:{d:"M864 256H736v-80c0-35.3-28.7-64-64-64H352c-35.3 0-64 28.7-64 64v80H160c-17.7 0-32 14.3-32 32v32c0 4.4 3.6 8 8 8h60.4l24.7 523c1.6 34.1 29.8 61 63.9 61h454c34.2 0 62.3-26.8 63.9-61l24.7-523H888c4.4 0 8-3.6 8-8v-32c0-17.7-14.3-32-32-32zm-200 0H360v-72h304v72z"}}]},name:"delete",theme:"filled"};var d=a(127029),c=function(e,t){return s.createElement(d.Z,Object.assign({},e,{ref:t,icon:i}))};c.displayName="DeleteFilled";const u=s.forwardRef(c);var p,m=a(853199),h=a(211965);e=a.hmd(e),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&p(e);var g,b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};!function(e){e[e.jsonUpload=0]="jsonUpload",e[e.copyPaste=1]="copyPaste"}(g||(g={}));const v={gsheets:"service_account_info",bigquery:"credentials_info"},f=e=>"true"===e;var y={name:"s5xdrg",styles:"display:flex;align-items:center"};const x=({changeMethods:e,isEditMode:t,db:a,editNewDb:i})=>{var d,c,p;const[b,x]=(0,s.useState)(g.jsonUpload.valueOf()),[C,Z]=(0,s.useState)(null),[_,w]=(0,s.useState)(!0),D="gsheets"===(null==a?void 0:a.engine)?!t&&!_:!t,P=t&&"{}"!==(null==a?void 0:a.encrypted_extra),U=(null==a?void 0:a.engine)&&v[a.engine],S="object"==typeof(null==a||null==(d=a.parameters)?void 0:d[U])?JSON.stringify(null==a||null==(c=a.parameters)?void 0:c[U]):null==a||null==(p=a.parameters)?void 0:p[U];return(0,h.tZ)(m.sv,null,"gsheets"===(null==a?void 0:a.engine)&&(0,h.tZ)("div",{className:"catalog-type-select"},(0,h.tZ)(l.Z,{css:e=>(0,m.tu)(e),required:!0},(0,r.t)("Type of Google Sheets allowed")),(0,h.tZ)(o.Ph,{style:{width:"100%"},defaultValue:P?"false":"true",onChange:e=>w(f(e))},(0,h.tZ)(o.Ph.Option,{value:"true",key:1},(0,r.t)("Publicly shared sheets only")),(0,h.tZ)(o.Ph.Option,{value:"false",key:2},(0,r.t)("Public and privately shared sheets")))),D&&(0,h.tZ)(s.Fragment,null,(0,h.tZ)(l.Z,{required:!0},(0,r.t)("How do you want to enter service account credentials?")),(0,h.tZ)(o.Ph,{defaultValue:b,style:{width:"100%"},onChange:e=>x(e)},(0,h.tZ)(o.Ph.Option,{value:g.jsonUpload},(0,r.t)("Upload JSON file")),(0,h.tZ)(o.Ph.Option,{value:g.copyPaste},(0,r.t)("Copy and Paste JSON credentials")))),b===g.copyPaste||t||i?(0,h.tZ)("div",{className:"input-container"},(0,h.tZ)(l.Z,{required:!0},(0,r.t)("Service Account")),(0,h.tZ)("textarea",{className:"input-form",name:U,value:S,onChange:e.onParametersChange,placeholder:"Paste content of service credentials JSON file here"}),(0,h.tZ)("span",{className:"label-paste"},(0,r.t)("Copy and paste the entire service account .json file here"))):D&&(0,h.tZ)("div",{className:"input-container",css:e=>(0,m.bC)(e)},(0,h.tZ)("div",{css:y},(0,h.tZ)(l.Z,{required:!0},(0,r.t)("Upload Credentials")),(0,h.tZ)(n.Z,{tooltip:(0,r.t)("Use the JSON file you automatically downloaded when creating your service account."),viewBox:"0 0 24 24"})),!C&&(0,h.tZ)(o.zx,{className:"input-upload-btn",onClick:()=>{var e,t;return null==(e=document)||null==(t=e.getElementById("selectedFile"))?void 0:t.click()}},(0,r.t)("Choose File")),C&&(0,h.tZ)("div",{className:"input-upload-current"},C,(0,h.tZ)(u,{onClick:()=>{Z(null),e.onParametersChange({target:{name:U,value:""}})}})),(0,h.tZ)("input",{id:"selectedFile",className:"input-upload",type:"file",onChange:async t=>{var a,s;let r;t.target.files&&(r=t.target.files[0]),Z(null==(a=r)?void 0:a.name),e.onParametersChange({target:{type:null,name:U,value:await(null==(s=r)?void 0:s.text()),checked:!1}}),document.getElementById("selectedFile").value=null}})))};var C,Z;b(x,"useState{[uploadOption, setUploadOption](CredentialInfoOptions.jsonUpload.valueOf())}\nuseState{[fileToUpload, setFileToUpload](null)}\nuseState{[isPublic, setIsPublic](true)}"),(C="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(C.register(g,"CredentialInfoOptions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/EncryptedField.tsx"),C.register(v,"encryptedCredentialsMap","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/EncryptedField.tsx"),C.register(f,"castStringToBoolean","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/EncryptedField.tsx"),C.register(x,"EncryptedField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/EncryptedField.tsx")),(Z="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&Z(e)},833117:(e,t,a)=>{a.d(t,{O:()=>h});var s=a(667294),r=a(455867),o=a(187858),n=a(902857);const l={icon:{tag:"svg",attrs:{viewBox:"64 64 896 896",focusable:"false"},children:[{tag:"path",attrs:{d:"M563.8 512l262.5-312.9c4.4-5.2.7-13.1-6.1-13.1h-79.8c-4.7 0-9.2 2.1-12.3 5.7L511.6 449.8 295.1 191.7c-3-3.6-7.5-5.7-12.3-5.7H203c-6.8 0-10.5 7.9-6.1 13.1L459.4 512 196.9 824.9A7.95 7.95 0 00203 838h79.8c4.7 0 9.2-2.1 12.3-5.7l216.5-258.1 216.5 258.1c3 3.6 7.5 5.7 12.3 5.7h79.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z"}}]},name:"close",theme:"outlined"};var i=a(127029),d=function(e,t){return s.createElement(i.Z,Object.assign({},e,{ref:t,icon:l}))};d.displayName="CloseOutlined";const c=s.forwardRef(d);var u,p=a(853199),m=a(211965);e=a.hmd(e),(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&u(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const h=({required:e,changeMethods:t,getValidation:a,validationErrors:l,db:i})=>{const d=(null==i?void 0:i.catalog)||[],u=l||{};return(0,m.tZ)(p.ed,null,(0,m.tZ)("h4",{className:"gsheet-title"},(0,r.t)("Connect Google Sheets as tables to this database")),(0,m.tZ)("div",null,null==d?void 0:d.map(((l,i)=>{var p,h;return(0,m.tZ)(s.Fragment,null,(0,m.tZ)(n.Z,{className:"catalog-label",required:!0},(0,r.t)("Google Sheet Name and URL")),(0,m.tZ)("div",{className:"catalog-name"},(0,m.tZ)(o.Z,{className:"catalog-name-input",required:e,validationMethods:{onBlur:a},errorMessage:null==(p=u[i])?void 0:p.name,placeholder:(0,r.t)("Enter a name for this sheet"),onChange:e=>{t.onParametersChange({target:{type:`catalog-${i}`,name:"name",value:e.target.value}})},value:l.name}),(null==d?void 0:d.length)>1&&(0,m.tZ)(c,{className:"catalog-delete",onClick:()=>t.onRemoveTableCatalog(i)})),(0,m.tZ)(o.Z,{className:"catalog-name-url",required:e,validationMethods:{onBlur:a},errorMessage:null==(h=u[i])?void 0:h.url,placeholder:(0,r.t)("Paste the shareable Google Sheet URL here"),onChange:e=>t.onParametersChange({target:{type:`catalog-${i}`,name:"value",value:e.target.value}}),value:l.value}))})),(0,m.tZ)(p.OD,{className:"catalog-add-btn",onClick:()=>{t.onAddTableCatalog()}},"+ ",(0,r.t)("Add sheet"))))};var g,b;(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&g.register(h,"TableCatalog","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/TableCatalog.tsx"),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},809034:(e,t,a)=>{a.d(t,{N:()=>i}),a(667294);var s,r=a(455867),o=a(187858),n=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const l={account:{helpText:(0,r.t)("Copy the account name of that database you are trying to connect to."),placeholder:"e.g. world_population"},warehouse:{placeholder:"e.g. compute_wh",className:"form-group-w-50"},role:{placeholder:"e.g. AccountAdmin",className:"form-group-w-50"}},i=({required:e,changeMethods:t,getValidation:a,validationErrors:s,db:r,field:i})=>{var d;return(0,n.tZ)(o.Z,{id:i,name:i,required:e,value:null==r||null==(d=r.parameters)?void 0:d[i],validationMethods:{onBlur:a},errorMessage:null==s?void 0:s[i],placeholder:l[i].placeholder,helpText:l[i].helpText,label:i,onChange:t.onParametersChange,className:l[i].className||i})};var d,c;(d="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(d.register(l,"FIELD_TEXT_MAP","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/ValidatedInputField.tsx"),d.register(i,"validatedInputField","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/ValidatedInputField.tsx")),(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&c(e)},804904:(e,t,a)=>{a.d(t,{ZP:()=>b});var s,r=a(667294),o=a(523419),n=a(809034),l=a(709419),i=a(833117),d=a(853199),c=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const u=["host","port","database","username","password","database_name","credentials_info","service_account_info","catalog","query","encryption","account","warehouse","role"],p={host:o.FQ,port:o.xP,database:o.WT,username:o.qm,password:o.Uy,database_name:o.w_,query:o.Wj,encryption:o.mB,credentials_info:l.N,service_account_info:l.N,catalog:i.O,warehouse:n.N,role:n.N,account:n.N},m=({dbModel:{parameters:e},onParametersChange:t,onChange:a,onQueryChange:s,onParametersUploadFileChange:o,onAddTableCatalog:n,onRemoveTableCatalog:l,validationErrors:i,getValidation:m,db:h,isEditMode:g=!1,sslForced:b,editNewDb:v})=>(0,c.tZ)(r.Fragment,null,(0,c.tZ)("div",{css:e=>[d.$G,(0,d.ro)(e)]},e&&u.filter((t=>Object.keys(e.properties).includes(t)||"database_name"===t)).map((r=>{var d;return p[r]({required:null==(d=e.required)?void 0:d.includes(r),changeMethods:{onParametersChange:t,onChange:a,onQueryChange:s,onParametersUploadFileChange:o,onAddTableCatalog:n,onRemoveTableCatalog:l},validationErrors:i,getValidation:m,db:h,key:r,field:r,isEditMode:g,sslForced:b,editNewDb:v})})))),h=p,g=m,b=g;var v,f;(v="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(v.register(u,"FormFieldOrder","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/index.tsx"),v.register(p,"FORM_FIELD_MAP","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/index.tsx"),v.register(m,"DatabaseConnectionForm","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/index.tsx"),v.register(h,"FormFieldMap","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/index.tsx"),v.register(g,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/DatabaseConnectionForm/index.tsx")),(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&f(e)},222607:(e,t,a)=>{a.d(t,{Z:()=>h});var s,r=a(211965),o=(a(667294),a(294184)),n=a.n(o),l=a(455867),i=a(608272),d=a(849576),c=a(843700),u=a(853199);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const p=({db:e,onInputChange:t,onTextChange:a,onEditorChange:s,onExtraInputChange:o,onExtraEditorChange:p})=>{var m,h,g,b,v,f,y,x,C,Z,_;const w=!(null==e||!e.expose_in_sqllab),D=!!(null!=e&&e.allow_ctas||null!=e&&e.allow_cvas);return(0,r.tZ)(c.Z,{expandIconPosition:"right",accordion:!0,css:e=>(0,u.ls)(e)},(0,r.tZ)(c.Z.Panel,{header:(0,r.tZ)("div",null,(0,r.tZ)("h4",null,"SQL Lab"),(0,r.tZ)("p",{className:"helper"},"Adjust how this database will interact with SQL Lab.")),key:"1"},(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"expose_in_sqllab",indeterminate:!1,checked:!(null==e||!e.expose_in_sqllab),onChange:t,labelText:(0,l.t)("Expose database in SQL Lab")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Allow this database to be queried in SQL Lab")})),(0,r.tZ)(u.J7,{className:n()("expandable",{open:w,"ctas-open":D})},(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_ctas",indeterminate:!1,checked:!(null==e||!e.allow_ctas),onChange:t,labelText:(0,l.t)("Allow CREATE TABLE AS")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Allow creation of new tables based on queries")}))),(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_cvas",indeterminate:!1,checked:!(null==e||!e.allow_cvas),onChange:t,labelText:(0,l.t)("Allow CREATE VIEW AS")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Allow creation of new views based on queries")})),(0,r.tZ)(u.j5,{className:n()("expandable",{open:D})},(0,r.tZ)("div",{className:"control-label"},(0,l.t)("CTAS & CVAS SCHEMA")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("input",{type:"text",name:"force_ctas_schema",value:(null==e?void 0:e.force_ctas_schema)||"",placeholder:(0,l.t)("Create or select schema..."),onChange:t})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Force all tables and views to be created in this schema when clicking CTAS or CVAS in SQL Lab.")))),(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_dml",indeterminate:!1,checked:!(null==e||!e.allow_dml),onChange:t,labelText:(0,l.t)("Allow DML")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Allow manipulation of the database using non-SELECT statements such as UPDATE, DELETE, CREATE, etc.")}))),(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_multi_schema_metadata_fetch",indeterminate:!1,checked:!(null==e||!e.allow_multi_schema_metadata_fetch),onChange:t,labelText:(0,l.t)("Allow Multi Schema Metadata Fetch")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Allow SQL Lab to fetch a list of all tables and all views across all database schemas. For large data warehouse with thousands of tables, this can be expensive and put strain on the system.")}))),(0,r.tZ)(u.j5,{css:u.R6},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"cost_estimate_enabled",indeterminate:!1,checked:!(null==e||null==(m=e.extra_json)||!m.cost_estimate_enabled),onChange:o,labelText:(0,l.t)("Enable query cost estimation")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("For Presto and Postgres, shows a button to compute cost before running a query.")}))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allows_virtual_table_explore",indeterminate:!1,checked:!(null==e||null==(h=e.extra_json)||!h.allows_virtual_table_explore),onChange:o,labelText:(0,l.t)("Allow this database to be explored")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("When enabled, users are able to visualize SQL Lab results in Explore.")})))))),(0,r.tZ)(c.Z.Panel,{header:(0,r.tZ)("div",null,(0,r.tZ)("h4",null,"Performance"),(0,r.tZ)("p",{className:"helper"},"Adjust performance settings of this database.")),key:"2"},(0,r.tZ)(u.j5,{className:"mb-8"},(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Chart cache timeout")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("input",{type:"number",name:"cache_timeout",value:(null==e?void 0:e.cache_timeout)||"",placeholder:(0,l.t)("Enter duration in seconds"),onChange:t})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Duration (in seconds) of the caching timeout for charts of this database. A timeout of 0 indicates that the cache never expires. Note this defaults to the global timeout if undefined."))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Schema cache timeout")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("input",{type:"number",name:"schema_cache_timeout",value:(null==e||null==(g=e.extra_json)||null==(b=g.metadata_cache_timeout)?void 0:b.schema_cache_timeout)||"",placeholder:(0,l.t)("Enter duration in seconds"),onChange:o,"data-test":"schema-cache-timeout-test"})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Duration (in seconds) of the metadata caching timeout for schemas of this database. If left unset, the cache never expires."))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Table cache timeout")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("input",{type:"number",name:"table_cache_timeout",value:(null==e||null==(v=e.extra_json)||null==(f=v.metadata_cache_timeout)?void 0:f.table_cache_timeout)||"",placeholder:(0,l.t)("Enter duration in seconds"),onChange:o,"data-test":"table-cache-timeout-test"})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Duration (in seconds) of the metadata caching timeout for tables of this database. If left unset, the cache never expires. "))),(0,r.tZ)(u.j5,{css:(0,r.iv)({no_margin_bottom:u.R6},"","")},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_run_async",indeterminate:!1,checked:!(null==e||!e.allow_run_async),onChange:t,labelText:(0,l.t)("Asynchronous query execution")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Operate the database in asynchronous mode, meaning that the queries are executed on remote workers as opposed to on the web server itself. This assumes that you have a Celery worker setup as well as a results backend. Refer to the installation docs for more information.")}))),(0,r.tZ)(u.j5,{css:(0,r.iv)({no_margin_bottom:u.R6},"","")},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"cancel_query_on_windows_unload",indeterminate:!1,checked:!(null==e||null==(y=e.extra_json)||!y.cancel_query_on_windows_unload),onChange:o,labelText:(0,l.t)("Cancel query on window unload event")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("Terminate running queries when browser window closed or navigated to another page. Available for Presto, Hive, MySQL, Postgres and Snowflake databases.")})))),(0,r.tZ)(c.Z.Panel,{header:(0,r.tZ)("div",null,(0,r.tZ)("h4",null,"Security"),(0,r.tZ)("p",{className:"helper"},"Add extra connection information.")),key:"3"},(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Secure extra")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(u.YT,{name:"encrypted_extra",value:(null==e?void 0:e.encrypted_extra)||"",placeholder:(0,l.t)("Secure extra"),onChange:e=>s({json:e,name:"encrypted_extra"}),width:"100%",height:"160px"})),(0,r.tZ)("div",{className:"helper"},(0,r.tZ)("div",null,(0,l.t)("JSON string containing additional connection configuration. This is used to provide connection information for systems like Hive, Presto and BigQuery which do not conform to the username:password syntax normally used by SQLAlchemy.")))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Root certificate")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("textarea",{name:"server_cert",value:(null==e?void 0:e.server_cert)||"",placeholder:(0,l.t)("Enter CA_BUNDLE"),onChange:a})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Optional CA_BUNDLE contents to validate HTTPS requests. Only available on certain database engines."))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Schemas allowed for CSV upload")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)("input",{type:"text",name:"schemas_allowed_for_file_upload",value:((null==e||null==(x=e.extra_json)?void 0:x.schemas_allowed_for_file_upload)||[]).join(","),placeholder:"schema1,schema2",onChange:o})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("A comma-separated list of schemas that CSVs are allowed to upload to."))),(0,r.tZ)(u.j5,{css:(0,r.iv)({no_margin_bottom:u.R6},"","")},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"impersonate_user",indeterminate:!1,checked:!(null==e||!e.impersonate_user),onChange:t,labelText:(0,l.t)("Impersonate logged in user (Presto, Trino, Drill, Hive, and GSheets)")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("If Presto or Trino, all the queries in SQL Lab are going to be executed as the currently logged on user who must have permission to run them. If Hive and hive.server2.enable.doAs is enabled, will run the queries as service account, but impersonate the currently logged on user via hive.server2.proxy.user property.")}))),(0,r.tZ)(u.j5,{css:(0,r.iv)({...u.R6},"","")},(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(d.Z,{id:"allow_file_upload",indeterminate:!1,checked:!(null==e||!e.allow_file_upload),onChange:t,labelText:(0,l.t)("Allow data upload")}),(0,r.tZ)(i.Z,{tooltip:(0,l.t)("If selected, please set the schemas allowed for data upload in Extra.")})))),(0,r.tZ)(c.Z.Panel,{header:(0,r.tZ)("div",null,(0,r.tZ)("h4",null,"Other"),(0,r.tZ)("p",{className:"helper"},"Additional settings.")),key:"4"},(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Metadata Parameters")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(u.YT,{name:"metadata_params",value:(null==e||null==(C=e.extra_json)?void 0:C.metadata_params)||"",placeholder:(0,l.t)("Metadata Parameters"),onChange:e=>p({json:e,name:"metadata_params"}),width:"100%",height:"160px"})),(0,r.tZ)("div",{className:"helper"},(0,r.tZ)("div",null,(0,l.t)("The metadata_params object gets unpacked into the sqlalchemy.MetaData call.")))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label"},(0,l.t)("Engine Parameters")),(0,r.tZ)("div",{className:"input-container"},(0,r.tZ)(u.YT,{name:"engine_params",value:(null==e||null==(Z=e.extra_json)?void 0:Z.engine_params)||"",placeholder:(0,l.t)("Engine Parameters"),onChange:e=>p({json:e,name:"engine_params"}),width:"100%",height:"160px"})),(0,r.tZ)("div",{className:"helper"},(0,r.tZ)("div",null,(0,l.t)("The engine_params object gets unpacked into the sqlalchemy.create_engine call.")))),(0,r.tZ)(u.j5,null,(0,r.tZ)("div",{className:"control-label","data-test":"version-label-test"},(0,l.t)("Version")),(0,r.tZ)("div",{className:"input-container","data-test":"version-spinbutton-test"},(0,r.tZ)("input",{type:"number",name:"version",value:(null==e||null==(_=e.extra_json)?void 0:_.version)||"",placeholder:(0,l.t)("Version number"),onChange:o})),(0,r.tZ)("div",{className:"helper"},(0,l.t)("Specify the database version. This should be used with Presto in order to enable query cost estimation.")))))},m=p,h=m;var g,b;(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(g.register(p,"ExtraOptions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ExtraOptions.tsx"),g.register(m,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ExtraOptions.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},854790:(e,t,a)=>{a.d(t,{s:()=>d,Z:()=>h});var s,r=a(667294),o=a(34858),n=a(853199),l=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const i=(0,o.z)(),d=i?i.support:"https://superset.apache.org/docs/databases/installing-database-drivers",c={postgresql:"https://superset.apache.org/docs/databases/postgres",mssql:"https://superset.apache.org/docs/databases/sql-server",gsheets:"https://superset.apache.org/docs/databases/google-sheets"},u=e=>e?i?i[e]||i.default:c[e]?c[e]:`https://superset.apache.org/docs/databases/${e}`:null,p=({isLoading:e,isEditMode:t,useSqlAlchemyForm:a,hasConnectedDb:s,db:o,dbName:c,dbModel:p,editNewDb:m})=>{const h=(0,l.tZ)(n.mI,null,(0,l.tZ)(n._7,null,null==o?void 0:o.backend),(0,l.tZ)(n.ZM,null,c)),g=(0,l.tZ)(n.mI,null,(0,l.tZ)("p",{className:"helper-top"}," STEP 2 OF 2 "),(0,l.tZ)("h4",null,"Enter Primary Credentials"),(0,l.tZ)("p",{className:"helper-bottom"},"Need help? Learn how to connect your database"," ",(0,l.tZ)("a",{href:(null==i?void 0:i.default)||d,target:"_blank",rel:"noopener noreferrer"},"here"),".")),b=(0,l.tZ)(n.SS,null,(0,l.tZ)(n.mI,null,(0,l.tZ)("p",{className:"helper-top"}," STEP 3 OF 3 "),(0,l.tZ)("h4",{className:"step-3-text"},"Your database was successfully connected! Here are some optional settings for your database"),(0,l.tZ)("p",{className:"helper-bottom"},"Need help? Learn more about"," ",(0,l.tZ)("a",{href:u(null==o?void 0:o.engine),target:"_blank",rel:"noopener noreferrer"},"connecting to ",p.name,".")))),v=(0,l.tZ)(n.SS,null,(0,l.tZ)(n.mI,null,(0,l.tZ)("p",{className:"helper-top"}," STEP 2 OF 3 "),(0,l.tZ)("h4",null,"Enter the required ",p.name," credentials"),(0,l.tZ)("p",{className:"helper-bottom"},"Need help? Learn more about"," ",(0,l.tZ)("a",{href:u(null==o?void 0:o.engine),target:"_blank",rel:"noopener noreferrer"},"connecting to ",p.name,".")))),f=(0,l.tZ)(n.mI,null,(0,l.tZ)("div",{className:"select-db"},(0,l.tZ)("p",{className:"helper-top"}," STEP 1 OF 3 "),(0,l.tZ)("h4",null,"Select a database to connect")));return e?(0,l.tZ)(r.Fragment,null):t?h:a?g:s&&!m?b:o||m?v:f},m=p,h=m;var g,b;(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(g.register(i,"supersetTextDocs","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx"),g.register(d,"DOCUMENTATION_LINK","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx"),g.register(c,"irregularDocumentationLinks","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx"),g.register(u,"documentationLink","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx"),g.register(p,"ModalHeader","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx"),g.register(m,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/ModalHeader.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},89728:(e,t,a)=>{a.d(t,{Z:()=>p});var s,r=a(667294),o=a(455867),n=a(208911),l=a(835932),i=a(853199),d=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const c=({db:e,onInputChange:t,testConnection:a,conf:s,isEditMode:c=!1,testInProgress:u=!1})=>{let p,m;var h,g;return n.Z&&(p=null==(h=n.Z.DB_MODAL_SQLALCHEMY_FORM)?void 0:h.SQLALCHEMY_DOCS_URL,m=null==(g=n.Z.DB_MODAL_SQLALCHEMY_FORM)?void 0:g.SQLALCHEMY_DOCS_URL),(0,d.tZ)(r.Fragment,null,(0,d.tZ)(i.j5,null,(0,d.tZ)("div",{className:"control-label"},(0,o.t)("Display Name"),(0,d.tZ)("span",{className:"required"},"*")),(0,d.tZ)("div",{className:"input-container"},(0,d.tZ)("input",{type:"text",name:"database_name","data-test":"database-name-input",value:(null==e?void 0:e.database_name)||"",placeholder:(0,o.t)("Name your database"),onChange:t})),(0,d.tZ)("div",{className:"helper"},(0,o.t)("Pick a name to help you identify this database."))),(0,d.tZ)(i.j5,null,(0,d.tZ)("div",{className:"control-label"},(0,o.t)("SQLAlchemy URI"),(0,d.tZ)("span",{className:"required"},"*")),(0,d.tZ)("div",{className:"input-container"},(0,d.tZ)("input",{type:"text",name:"sqlalchemy_uri","data-test":"sqlalchemy-uri-input",value:(null==e?void 0:e.sqlalchemy_uri)||"",autoComplete:"off",placeholder:(0,o.t)("dialect+driver://username:password@host:port/database"),onChange:t})),(0,d.tZ)("div",{className:"helper"},(0,o.t)("Refer to the")," ",(0,d.tZ)("a",{href:p||(null==s?void 0:s.SQLALCHEMY_DOCS_URL)||"",target:"_blank",rel:"noopener noreferrer"},m||(null==s?void 0:s.SQLALCHEMY_DISPLAY_TEXT)||"")," ",(0,o.t)("for more information on how to structure your URI."))),(0,d.tZ)(l.Z,{onClick:a,disabled:u,cta:!0,buttonStyle:"link",css:e=>(0,i.Gy)(e)},(0,o.t)("Test connection")))},u=c,p=u;var m,h;(m="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(m.register(c,"SqlAlchemyTab","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/SqlAlchemyForm.tsx"),m.register(u,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/SqlAlchemyForm.tsx")),(h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&h(e)},603506:(e,t,a)=>{a.d(t,{Z:()=>$});var s,r=a(294435),o=a.n(r),n=a(455867),l=a(593185),i=a(667294),d=a(940637),c=a(582191),u=a(229487),p=a(574520),m=a(835932),h=a(789719),g=a(608272),b=a(414114),v=a(34858),f=a(301483),y=a(163727),x=a(838703),C=a(222607),Z=a(89728),_=a(804904),w=a(853199),D=a(854790),P=a(211965);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e);var U="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const S={gsheets:{message:"Why do I need to create a database?",description:"To begin using your Google Sheets, you need to create a database first. Databases are used as a way to identify your data so that it can be queried and visualized. This database will hold all of your individual Google Sheets you choose to connect here."}},L={CONNECTION_MISSING_PARAMETERS_ERROR:{message:(0,n.t)("Missing Required Fields"),description:(0,n.t)("Please complete all required fields.")},CONNECTION_INVALID_HOSTNAME_ERROR:{message:(0,n.t)("Could not verify the host"),description:(0,n.t)("The host is invalid. Please verify that this field is entered correctly.")},CONNECTION_PORT_CLOSED_ERROR:{message:(0,n.t)("Port is closed"),description:(0,n.t)("Please verify that port is open to connect.")},CONNECTION_INVALID_PORT_ERROR:{message:(0,n.t)("Invalid Port Number"),description:(0,n.t)("The port must be a whole number less than or equal to 65535.")},CONNECTION_ACCESS_DENIED_ERROR:{message:(0,n.t)("Invalid account information"),description:(0,n.t)("Either the username or password is incorrect.")},CONNECTION_INVALID_PASSWORD_ERROR:{message:(0,n.t)("Invalid account information"),description:(0,n.t)("Either the username or password is incorrect.")},INVALID_PAYLOAD_SCHEMA_ERROR:{message:(0,n.t)("Incorrect Fields"),description:(0,n.t)("Please make sure all fields are filled out correctly")},TABLE_DOES_NOT_EXIST_ERROR:{message:(0,n.t)("URL could not be identified"),description:(0,n.t)('The URL could not be identified. Please check for typos and make sure that "Type of google sheet allowed" selection matches the input')}};var M;function E(e,t){var a,s,r,n;const l={...e||{}};let i,d={},c="",u={};switch(t.type){case M.extraEditorChange:return{...l,extra_json:{...l.extra_json,[t.payload.name]:t.payload.json}};case M.extraInputChange:var p;return"schema_cache_timeout"===t.payload.name||"table_cache_timeout"===t.payload.name?{...l,extra_json:{...l.extra_json,metadata_cache_timeout:{...null==(p=l.extra_json)?void 0:p.metadata_cache_timeout,[t.payload.name]:t.payload.value}}}:"schemas_allowed_for_file_upload"===t.payload.name?{...l,extra_json:{...l.extra_json,schemas_allowed_for_file_upload:(t.payload.value||"").split(",")}}:{...l,extra_json:{...l.extra_json,[t.payload.name]:"checkbox"===t.payload.type?t.payload.checked:t.payload.value}};case M.inputChange:return"checkbox"===t.payload.type?{...l,[t.payload.name]:t.payload.checked}:{...l,[t.payload.name]:t.payload.value};case M.parametersChange:if(void 0!==l.catalog&&null!=(a=t.payload.type)&&a.startsWith("catalog")){var m,h;const e=null==(m=t.payload.type)?void 0:m.split("-")[1];((null==l?void 0:l.catalog[e])||{})[t.payload.name]=t.payload.value;const a={};return null==(h=l.catalog)||h.map((e=>{a[e.name]=e.value})),{...l,parameters:{...l.parameters,catalog:a}}}return{...l,parameters:{...l.parameters,[t.payload.name]:t.payload.value}};case M.addTableCatalogSheet:return void 0!==l.catalog?{...l,catalog:[...l.catalog,{name:"",value:""}]}:{...l,catalog:[{name:"",value:""}]};case M.removeTableCatalogSheet:return null==(s=l.catalog)||s.splice(t.payload.indexToDelete,1),{...l};case M.editorChange:return{...l,[t.payload.name]:t.payload.json};case M.queryChange:return{...l,parameters:{...l.parameters,query:Object.fromEntries(new(o())(t.payload.value))},query_input:t.payload.value};case M.textChange:return{...l,[t.payload.name]:t.payload.value};case M.fetched:var g,b,v;if(t.payload.extra&&(i={...JSON.parse(t.payload.extra||"")},u={...JSON.parse(t.payload.extra||""),metadata_params:JSON.stringify(null==(g=i)?void 0:g.metadata_params),engine_params:JSON.stringify(null==(b=i)?void 0:b.engine_params),schemas_allowed_for_file_upload:null==(v=i)?void 0:v.schemas_allowed_for_file_upload}),d=(null==(r=t.payload)||null==(n=r.parameters)?void 0:n.query)||{},c=Object.entries(d).map((([e,t])=>`${e}=${t}`)).join("&"),t.payload.encrypted_extra&&t.payload.configuration_method===y.j.DYNAMIC_FORM){var f,x;const e=Object.keys((null==(f=i)||null==(x=f.engine_params)?void 0:x.catalog)||{}).map((e=>{var t,a;return{name:e,value:null==(t=i)||null==(a=t.engine_params)?void 0:a.catalog[e]}}));return{...t.payload,engine:t.payload.backend||l.engine,configuration_method:t.payload.configuration_method,extra_json:u,catalog:e,parameters:t.payload.parameters,query_input:c}}return{...t.payload,encrypted_extra:t.payload.encrypted_extra||"",engine:t.payload.backend||l.engine,configuration_method:t.payload.configuration_method,extra_json:u,parameters:t.payload.parameters,query_input:c};case M.dbSelected:case M.configMethodChange:return{...t.payload};case M.reset:default:return null}}!function(e){e[e.configMethodChange=0]="configMethodChange",e[e.dbSelected=1]="dbSelected",e[e.editorChange=2]="editorChange",e[e.fetched=3]="fetched",e[e.inputChange=4]="inputChange",e[e.parametersChange=5]="parametersChange",e[e.reset=6]="reset",e[e.textChange=7]="textChange",e[e.extraInputChange=8]="extraInputChange",e[e.extraEditorChange=9]="extraEditorChange",e[e.addTableCatalogSheet=10]="addTableCatalogSheet",e[e.removeTableCatalogSheet=11]="removeTableCatalogSheet",e[e.queryChange=12]="queryChange"}(M||(M={}));const N="1",R=e=>JSON.stringify({...e,metadata_params:JSON.parse((null==e?void 0:e.metadata_params)||"{}"),engine_params:JSON.parse((null==e?void 0:e.engine_params)||"{}"),schemas_allowed_for_file_upload:((null==e?void 0:e.schemas_allowed_for_file_upload)||[]).filter((e=>""!==e))}),H=({addDangerToast:e,addSuccessToast:t,onDatabaseAdd:a,onHide:s,show:r,databaseId:o,dbEngine:b})=>{var U;const[H,j]=(0,i.useReducer)(E,null),[$,T]=(0,i.useState)(N),[A,k]=(0,v.cb)(),[O,G,I]=(0,v.h1)(),[F,q]=(0,i.useState)(!1),[z,B]=(0,i.useState)(""),[Q,V]=(0,i.useState)(!1),[Y,K]=(0,i.useState)(!1),[J,W]=(0,i.useState)(!1),X=(0,f.c)(),ee=(0,v.rM)(),te=(0,v.jb)(),ae=!!o,se=(0,l.c)(l.T.FORCE_DATABASE_CONNECTIONS_SSL),re=te||!(null==H||!H.engine||!S[H.engine]),oe=(null==H?void 0:H.configuration_method)===y.j.SQLALCHEMY_URI,ne=ae||oe,{state:{loading:le,resource:ie,error:de},fetchResource:ce,createResource:ue,updateResource:pe,clearError:me}=(0,v.LE)("database",(0,n.t)("database"),e),he=O||de,ge=e=>e&&0===Object.keys(e).length,be=(null==A||null==(U=A.databases)?void 0:U.find((e=>e.engine===(ae?null==H?void 0:H.backend:null==H?void 0:H.engine))))||{},ve=()=>{j({type:M.reset}),q(!1),I(null),me(),V(!1),s()},fe=async()=>{var e;const{id:s,...r}=H||{},o=JSON.parse(JSON.stringify(r));if(o.configuration_method===y.j.DYNAMIC_FORM){if(await G(o,!0),O&&!ge(O))return;const e=ae?o.parameters_schema.properties:null==be?void 0:be.parameters.properties,t=JSON.parse(o.encrypted_extra||"{}");Object.keys(e||{}).forEach((a=>{var s,r,n,l;e[a]["x-encrypted-extra"]&&null!=(s=o.parameters)&&s[a]&&("object"==typeof(null==(r=o.parameters)?void 0:r[a])?(t[a]=null==(n=o.parameters)?void 0:n[a],o.parameters[a]=JSON.stringify(o.parameters[a])):t[a]=JSON.parse((null==(l=o.parameters)?void 0:l[a])||"{}"))})),o.encrypted_extra=JSON.stringify(t),"gsheets"===o.engine&&(o.impersonate_user=!0)}null!=o&&null!=(e=o.parameters)&&e.catalog&&(o.extra_json={engine_params:JSON.stringify({catalog:o.parameters.catalog})}),null!=o&&o.extra_json&&(o.extra=R(null==o?void 0:o.extra_json)),null!=H&&H.id?(K(!0),await pe(H.id,o,o.configuration_method===y.j.DYNAMIC_FORM)&&(a&&a(),Q||(ve(),t((0,n.t)("Database settings updated"))))):H&&(K(!0),await ue(o,o.configuration_method===y.j.DYNAMIC_FORM)&&(q(!0),a&&a(),ne&&(ve(),t((0,n.t)("Database connected"))))),V(!1),K(!1)},ye=(e,t)=>{j({type:e,payload:t})},xe=e=>{if("Other"===e)j({type:M.dbSelected,payload:{database_name:e,configuration_method:y.j.SQLALCHEMY_URI,engine:void 0}});else{const t=null==A?void 0:A.databases.filter((t=>t.name===e))[0],{engine:a,parameters:s}=t,r=void 0!==s;j({type:M.dbSelected,payload:{database_name:e,engine:a,configuration_method:r?y.j.DYNAMIC_FORM:y.j.SQLALCHEMY_URI}})}j({type:M.addTableCatalogSheet})},Ce=()=>{ie&&ce(ie.id),V(!0)},Ze=()=>{Q&&q(!1),j({type:M.reset})},_e=()=>H?!F||Q?(0,P.tZ)(i.Fragment,null,(0,P.tZ)(w.OD,{key:"back",onClick:Ze},(0,n.t)("Back")),(0,P.tZ)(w.OD,{key:"submit",buttonStyle:"primary",onClick:fe},(0,n.t)("Connect"))):(0,P.tZ)(i.Fragment,null,(0,P.tZ)(w.OD,{key:"back",onClick:Ce},(0,n.t)("Back")),(0,P.tZ)(w.OD,{key:"submit",buttonStyle:"primary",onClick:fe,"data-test":"modal-confirm-button"},(0,n.t)("Finish"))):[];(0,i.useEffect)((()=>{r&&(T(N),k(),K(!0)),o&&r&&ae&&o&&(le||ce(o).catch((t=>e((0,n.t)("Sorry there was an error fetching database information: %s",t.message)))))}),[r,o]),(0,i.useEffect)((()=>{ie&&(j({type:M.fetched,payload:ie}),B(ie.database_name))}),[ie]),(0,i.useEffect)((()=>{Y&&K(!1),A&&b&&xe(b)}),[A]);const we=()=>{if(ge(de)||ge(O)&&!((null==O?void 0:O.error_type)in L))return(0,P.tZ)(i.Fragment,null);var e,t;if(O)return(0,P.tZ)(u.Z,{type:"error",css:e=>(0,w.gH)(e),message:(null==(e=L[null==O?void 0:O.error_type])?void 0:e.message)||(null==O?void 0:O.error_type),description:(null==(t=L[null==O?void 0:O.error_type])?void 0:t.description)||JSON.stringify(O),showIcon:!0,closable:!1});const a="object"==typeof de?Object.values(de):[];return(0,P.tZ)(u.Z,{type:"error",css:e=>(0,w.gH)(e),message:(0,n.t)("Database Creation Error"),description:(null==a?void 0:a[0])||de})};return ne?(0,P.tZ)(p.Z,{css:e=>[w.B2,w.jo,(0,w.fj)(e),(0,w.qS)(e),(0,w.xk)(e)],name:"database","data-test":"database-modal",onHandledPrimaryAction:fe,onHide:ve,primaryButtonName:ae?(0,n.t)("Save"):(0,n.t)("Connect"),width:"500px",centered:!0,show:r,title:(0,P.tZ)("h4",null,ae?(0,n.t)("Edit database"):(0,n.t)("Connect a database")),footer:ae?(0,P.tZ)(i.Fragment,null,(0,P.tZ)(w.OD,{key:"close",onClick:ve},(0,n.t)("Close")),(0,P.tZ)(w.OD,{key:"submit",buttonStyle:"primary",onClick:fe},(0,n.t)("Finish"))):_e()},(0,P.tZ)(w.SS,null,(0,P.tZ)(w.GK,null,(0,P.tZ)(D.Z,{isLoading:Y,isEditMode:ae,useSqlAlchemyForm:oe,hasConnectedDb:F,db:H,dbName:z,dbModel:be}))),(0,P.tZ)(d.ZP,{defaultActiveKey:N,activeKey:$,onTabClick:e=>{T(e)},animated:{inkBar:!0,tabPane:!0}},(0,P.tZ)(d.ZP.TabPane,{tab:(0,P.tZ)("span",null,(0,n.t)("Basic")),key:"1"},oe?(0,P.tZ)(w.LC,null,(0,P.tZ)(Z.Z,{db:H,onInputChange:({target:e})=>ye(M.inputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),conf:X,testConnection:()=>{var a;if(null==H||!H.sqlalchemy_uri)return void e((0,n.t)("Please enter a SQLAlchemy URI to test"));const s={sqlalchemy_uri:(null==H?void 0:H.sqlalchemy_uri)||"",database_name:(null==H||null==(a=H.database_name)?void 0:a.trim())||void 0,impersonate_user:(null==H?void 0:H.impersonate_user)||void 0,extra:R(null==H?void 0:H.extra_json)||void 0,encrypted_extra:(null==H?void 0:H.encrypted_extra)||"",server_cert:(null==H?void 0:H.server_cert)||void 0};W(!0),(0,v.xx)(s,(t=>{W(!1),e(t)}),(e=>{W(!1),t(e)}))},isEditMode:ae,testInProgress:J}),(Se=(null==H?void 0:H.backend)||(null==H?void 0:H.engine),void 0!==(null==A||null==(Le=A.databases)||null==(Me=Le.find((e=>e.backend===Se||e.engine===Se)))?void 0:Me.parameters)&&!ae&&(0,P.tZ)("div",{css:e=>(0,w.bC)(e)},(0,P.tZ)(m.Z,{buttonStyle:"link",onClick:()=>j({type:M.configMethodChange,payload:{database_name:null==H?void 0:H.database_name,configuration_method:y.j.DYNAMIC_FORM,engine:null==H?void 0:H.engine}}),css:e=>(0,w.iz)(e)},(0,n.t)("Connect this database using the dynamic form instead")),(0,P.tZ)(g.Z,{tooltip:(0,n.t)("Click this link to switch to an alternate form that exposes only the required fields needed to connect this database."),viewBox:"0 -6 24 24"})))):(0,P.tZ)(_.ZP,{isEditMode:!0,sslForced:se,dbModel:be,db:H,onParametersChange:({target:e})=>ye(M.parametersChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),onChange:({target:e})=>ye(M.textChange,{name:e.name,value:e.value}),onQueryChange:({target:e})=>ye(M.queryChange,{name:e.name,value:e.value}),onAddTableCatalog:()=>j({type:M.addTableCatalogSheet}),onRemoveTableCatalog:e=>j({type:M.removeTableCatalogSheet,payload:{indexToDelete:e}}),getValidation:()=>G(H),validationErrors:O}),!ae&&(0,P.tZ)(w.u_,null,(0,P.tZ)(u.Z,{closable:!1,css:e=>(0,w.Yd)(e),message:"Additional fields may be required",showIcon:!0,description:(0,P.tZ)(i.Fragment,null,(0,n.t)("Select databases require additional fields to be completed in the Advanced tab to successfully connect the database. Learn what requirements your databases has "),(0,P.tZ)("a",{href:D.s,target:"_blank",rel:"noopener noreferrer",className:"additional-fields-alert-description"},(0,n.t)("here")),"."),type:"info"}))),(0,P.tZ)(d.ZP.TabPane,{tab:(0,P.tZ)("span",null,(0,n.t)("Advanced")),key:"2"},(0,P.tZ)(C.Z,{db:H,onInputChange:({target:e})=>ye(M.inputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),onTextChange:({target:e})=>ye(M.textChange,{name:e.name,value:e.value}),onEditorChange:e=>ye(M.editorChange,e),onExtraInputChange:({target:e})=>{ye(M.extraInputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value})},onExtraEditorChange:e=>{ye(M.extraEditorChange,e)}}),he&&we()))):(0,P.tZ)(p.Z,{css:e=>[w.jo,(0,w.fj)(e),(0,w.qS)(e),(0,w.xk)(e)],name:"database",onHandledPrimaryAction:fe,onHide:ve,primaryButtonName:F?(0,n.t)("Finish"):(0,n.t)("Connect"),width:"500px",centered:!0,show:r,title:(0,P.tZ)("h4",null,(0,n.t)("Connect a database")),footer:_e()},F?(0,P.tZ)(i.Fragment,null,(0,P.tZ)(D.Z,{isLoading:Y,isEditMode:ae,useSqlAlchemyForm:oe,hasConnectedDb:F,db:H,dbName:z,dbModel:be,editNewDb:Q}),Q?(0,P.tZ)(_.ZP,{isEditMode:!0,sslForced:se,dbModel:be,db:H,onParametersChange:({target:e})=>ye(M.parametersChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),onChange:({target:e})=>ye(M.textChange,{name:e.name,value:e.value}),onQueryChange:({target:e})=>ye(M.queryChange,{name:e.name,value:e.value}),onAddTableCatalog:()=>j({type:M.addTableCatalogSheet}),onRemoveTableCatalog:e=>j({type:M.removeTableCatalogSheet,payload:{indexToDelete:e}}),getValidation:()=>G(H),validationErrors:O}):(0,P.tZ)(C.Z,{db:H,onInputChange:({target:e})=>ye(M.inputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),onTextChange:({target:e})=>ye(M.textChange,{name:e.name,value:e.value}),onEditorChange:e=>ye(M.editorChange,e),onExtraInputChange:({target:e})=>{ye(M.extraInputChange,{type:e.type,name:e.name,checked:e.checked,value:e.value})},onExtraEditorChange:e=>ye(M.extraEditorChange,e)})):(0,P.tZ)(i.Fragment,null,!Y&&(H?(0,P.tZ)(i.Fragment,null,(0,P.tZ)(D.Z,{isLoading:Y,isEditMode:ae,useSqlAlchemyForm:oe,hasConnectedDb:F,db:H,dbName:z,dbModel:be}),re&&(()=>{var e,t,a,s,r;const{hostname:o}=window.location;let n=(null==te||null==(e=te.REGIONAL_IPS)?void 0:e.default)||"";const l=(null==te?void 0:te.REGIONAL_IPS)||{};return Object.entries(l).forEach((([e,t])=>{const a=new RegExp(e);o.match(a)&&(n=t)})),(null==H?void 0:H.engine)&&(0,P.tZ)(w.u_,null,(0,P.tZ)(u.Z,{closable:!1,css:e=>(0,w.Yd)(e),type:"info",showIcon:!0,message:(null==(t=S[H.engine])?void 0:t.message)||(null==te||null==(a=te.DEFAULT)?void 0:a.message),description:(null==(s=S[H.engine])?void 0:s.description)||(null==te||null==(r=te.DEFAULT)?void 0:r.description)+n}))})(),(0,P.tZ)(_.ZP,{db:H,sslForced:se,dbModel:be,onAddTableCatalog:()=>{j({type:M.addTableCatalogSheet})},onQueryChange:({target:e})=>ye(M.queryChange,{name:e.name,value:e.value}),onRemoveTableCatalog:e=>{j({type:M.removeTableCatalogSheet,payload:{indexToDelete:e}})},onParametersChange:({target:e})=>ye(M.parametersChange,{type:e.type,name:e.name,checked:e.checked,value:e.value}),onChange:({target:e})=>ye(M.textChange,{name:e.name,value:e.value}),getValidation:()=>G(H),validationErrors:O}),(0,P.tZ)("div",{css:e=>(0,w.bC)(e)},(0,P.tZ)(m.Z,{"data-test":"sqla-connect-btn",buttonStyle:"link",onClick:()=>j({type:M.configMethodChange,payload:{engine:H.engine,configuration_method:y.j.SQLALCHEMY_URI,database_name:H.database_name}}),css:w.Hd},(0,n.t)("Connect this database with a SQLAlchemy URI string instead")),(0,P.tZ)(g.Z,{tooltip:(0,n.t)("Click this link to switch to an alternate form that allows you to input the SQLAlchemy URL for this database manually."),viewBox:"0 -6 24 24"})),he&&we()):(0,P.tZ)(w.Q0,null,(0,P.tZ)(D.Z,{isLoading:Y,isEditMode:ae,useSqlAlchemyForm:oe,hasConnectedDb:F,db:H,dbName:z,dbModel:be}),(0,P.tZ)("div",{className:"preferred"},null==A||null==(Ue=A.databases)?void 0:Ue.filter((e=>e.preferred)).map((e=>(0,P.tZ)(h.Z,{className:"preferred-item",onClick:()=>xe(e.name),buttonText:e.name,icon:null==ee?void 0:ee[e.engine]})))),(0,P.tZ)("div",{className:"available"},(0,P.tZ)("h4",{className:"available-label"},(0,n.t)("Or choose from a list of other databases we support:")),(0,P.tZ)("div",{className:"control-label"},(0,n.t)("Supported databases")),(0,P.tZ)(c.Ph,{className:"available-select",onChange:xe,placeholder:(0,n.t)("Choose a database...")},null==(De=[...(null==A?void 0:A.databases)||[]])?void 0:De.sort(((e,t)=>e.name.localeCompare(t.name))).map((e=>(0,P.tZ)(c.Ph.Option,{value:e.name,key:e.name},e.name))),(0,P.tZ)(c.Ph.Option,{value:"Other",key:"Other"},(0,n.t)("Other"))),(0,P.tZ)(u.Z,{showIcon:!0,closable:!1,css:e=>(0,w.Yd)(e),type:"info",message:(null==te||null==(Pe=te.ADD_DATABASE)?void 0:Pe.message)||(0,n.t)("Want to add a new database?"),description:null!=te&&te.ADD_DATABASE?(0,P.tZ)(i.Fragment,null,(0,n.t)("Any databases that allow connections via SQL Alchemy URIs can be added. "),(0,P.tZ)("a",{href:null==te?void 0:te.ADD_DATABASE.contact_link,target:"_blank",rel:"noopener noreferrer"},null==te?void 0:te.ADD_DATABASE.contact_description_link)," ",null==te?void 0:te.ADD_DATABASE.description):(0,P.tZ)(i.Fragment,null,(0,n.t)("Any databases that allow connections via SQL Alchemy URIs can be added. Learn about how to connect a database driver "),(0,P.tZ)("a",{href:D.s,target:"_blank",rel:"noopener noreferrer"},(0,n.t)("here")),".")}))))),Y&&(0,P.tZ)(x.Z,null));var De,Pe,Ue,Se,Le,Me};U(H,"useReducer{[db, setDB](null)}\nuseState{[tabKey, setTabKey](DEFAULT_TAB_KEY)}\nuseAvailableDatabases{[availableDbs, getAvailableDbs]}\nuseDatabaseValidation{[validationErrors, getValidation, setValidationErrors]}\nuseState{[hasConnectedDb, setHasConnectedDb](false)}\nuseState{[dbName, setDbName]('')}\nuseState{[editNewDb, setEditNewDb](false)}\nuseState{[isLoading, setLoading](false)}\nuseState{[testInProgress, setTestInProgress](false)}\nuseCommonConf{conf}\nuseSingleViewResource{{ state: { loading: dbLoading, resource: dbFetched, error: dbErrors }, fetchResource, createResource, updateResource, clearError, }}\nuseEffect{}\nuseEffect{}\nuseEffect{}",(()=>[v.cb,v.h1,f.c,v.LE]));const j=(0,b.Z)(H),$=j;var T,A;(T="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(T.register(S,"engineSpecificAlertMapping","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(L,"errorAlertMapping","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(M,"ActionType","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(E,"dbReducer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(N,"DEFAULT_TAB_KEY","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(R,"serializeExtra","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(H,"DatabaseModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx"),T.register(j,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/index.tsx")),(A="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&A(e)},853199:(e,t,a)=>{a.d(t,{R6:()=>i,tu:()=>d,mI:()=>c,ls:()=>u,B2:()=>p,jo:()=>m,bC:()=>h,ob:()=>g,$G:()=>b,fj:()=>v,Yd:()=>f,u_:()=>y,gH:()=>x,qS:()=>C,Gy:()=>Z,xk:()=>_,ro:()=>w,j5:()=>D,YT:()=>P,J7:()=>U,LC:()=>S,Hd:()=>L,iz:()=>M,GK:()=>E,_7:()=>H,ZM:()=>j,sv:()=>$,Q0:()=>T,OD:()=>A,SS:()=>k,ed:()=>O});var s,r=a(211965),o=a(751995),n=a(794670),l=a(835932);e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const i=r.iv`
  margin-bottom: 0;
`,d=e=>r.iv`
  margin-bottom: ${2*e.gridUnit}px;
`,c=o.iK.header`
  border-bottom: ${({theme:e})=>`${.25*e.gridUnit}px solid\n    ${e.colors.grayscale.light2};`}
  padding: ${({theme:e})=>2*e.gridUnit}px
    ${({theme:e})=>4*e.gridUnit}px;
  line-height: ${({theme:e})=>6*e.gridUnit}px;

  .helper-top {
    padding-bottom: 0;
    color: ${({theme:e})=>e.colors.grayscale.base};
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
    margin: 0;
  }

  .helper-bottom {
    padding-top: 0;
    color: ${({theme:e})=>e.colors.grayscale.base};
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
    margin: 0;
  }

  h4 {
    color: ${({theme:e})=>e.colors.grayscale.dark2};
    font-weight: bold;
    font-size: ${({theme:e})=>e.typography.sizes.l}px;
    margin: 0;
    padding: 0;
    line-height: ${({theme:e})=>8*e.gridUnit}px;
  }

  .select-db {
    padding-bottom: ${({theme:e})=>2*e.gridUnit}px;
    .helper {
      margin: 0;
    }

    h4 {
      margin: 0 0 ${({theme:e})=>4*e.gridUnit}px;
    }
  }
`,u=e=>r.iv`
  .ant-collapse-header {
    padding-top: ${3.5*e.gridUnit}px;
    padding-bottom: ${2.5*e.gridUnit}px;

    .anticon.ant-collapse-arrow {
      top: calc(50% - ${6}px);
    }
    .helper {
      color: ${e.colors.grayscale.base};
    }
  }
  h4 {
    font-size: 16px;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: ${e.gridUnit}px;
  }
  p.helper {
    margin-bottom: 0;
    padding: 0;
  }
`,p=r.iv`
  .ant-tabs-top {
    margin-top: 0;
  }
  .ant-tabs-top > .ant-tabs-nav {
    margin-bottom: 0;
  }
  .ant-tabs-tab {
    margin-right: 0;
  }
`,m=r.iv`
  .ant-modal-body {
    padding-left: 0;
    padding-right: 0;
    padding-top: 0;
  }
`,h=e=>r.iv`
  margin-bottom: ${5*e.gridUnit}px;
  svg {
    margin-bottom: ${.25*e.gridUnit}px;
  }
`,g=e=>r.iv`
  padding-left: ${2*e.gridUnit}px;
`,b=e=>r.iv`
  padding: ${4*e.gridUnit}px ${4*e.gridUnit}px 0;
`,v=e=>r.iv`
  .ant-select-dropdown {
    height: ${40*e.gridUnit}px;
  }

  .ant-modal-header {
    padding: ${4.5*e.gridUnit}px ${4*e.gridUnit}px
      ${4*e.gridUnit}px;
  }

  .ant-modal-close-x .close {
    color: ${e.colors.grayscale.dark1};
    opacity: 1;
  }

  .ant-modal-title > h4 {
    font-weight: bold;
  }

  .ant-modal-body {
    height: ${180.5*e.gridUnit}px;
  }

  .ant-modal-footer {
    height: ${16.25*e.gridUnit}px;
  }
`,f=e=>r.iv`
  border: 1px solid ${e.colors.info.base};
  padding: ${4*e.gridUnit}px;
  margin: ${4*e.gridUnit}px 0;

  .ant-alert-message {
    color: ${e.colors.info.dark2};
    font-size: ${e.typography.sizes.s+1}px;
    font-weight: bold;
  }

  .ant-alert-description {
    color: ${e.colors.info.dark2};
    font-size: ${e.typography.sizes.s+1}px;
    line-height: ${4*e.gridUnit}px;

    a {
      text-decoration: underline;
    }

    .ant-alert-icon {
      margin-right: ${2.5*e.gridUnit}px;
      font-size: ${e.typography.sizes.l+1}px;
      position: relative;
      top: ${e.gridUnit/4}px;
    }
  }
`,y=o.iK.div`
  margin: 0 ${({theme:e})=>4*e.gridUnit}px -${({theme:e})=>4*e.gridUnit}px;
`,x=e=>r.iv`
  border: ${e.colors.error.base} 1px solid;
  padding: ${4*e.gridUnit}px;
  margin: ${8*e.gridUnit}px ${4*e.gridUnit}px;
  color: ${e.colors.error.dark2};
  .ant-alert-message {
    font-size: ${e.typography.sizes.s+1}px;
    font-weight: bold;
  }
  .ant-alert-description {
    font-size: ${e.typography.sizes.s+1}px;
    line-height: ${4*e.gridUnit}px;
    .ant-alert-icon {
      margin-right: ${2.5*e.gridUnit}px;
      font-size: ${e.typography.sizes.l+1}px;
      position: relative;
      top: ${e.gridUnit/4}px;
    }
  }
`,C=e=>r.iv`
  .required {
    margin-left: ${e.gridUnit/2}px;
    color: ${e.colors.error.base};
  }

  .helper {
    display: block;
    padding: ${e.gridUnit}px 0;
    color: ${e.colors.grayscale.light1};
    font-size: ${e.typography.sizes.s-1}px;
    text-align: left;
  }
`,Z=e=>r.iv`
  width: 100%;
  border: 1px solid ${e.colors.primary.dark2};
  color: ${e.colors.primary.dark2};
  &:hover,
  &:focus {
    border: 1px solid ${e.colors.primary.dark1};
    color: ${e.colors.primary.dark1};
  }
`,_=e=>r.iv`
  .form-group {
    margin-bottom: ${4*e.gridUnit}px;
    &-w-50 {
      display: inline-block;
      width: ${`calc(50% - ${4*e.gridUnit}px)`};
      & + .form-group-w-50 {
        margin-left: ${8*e.gridUnit}px;
        margin-bottom: ${10*e.gridUnit}px;
      }
    }
  }
  .control-label {
    color: ${e.colors.grayscale.dark1};
    font-size: ${e.typography.sizes.s-1}px;
  }
  .helper {
    color: ${e.colors.grayscale.light1};
    font-size: ${e.typography.sizes.s-1}px;
    margin-top: ${1.5*e.gridUnit}px;
  }
  .ant-tabs-content-holder {
    overflow: auto;
    max-height: 475px;
  }
`,w=e=>r.iv`
  label {
    color: ${e.colors.grayscale.dark1};
    font-size: ${e.typography.sizes.s-1}px;
    margin-bottom: 0;
  }
`,D=o.iK.div`
  margin-bottom: ${({theme:e})=>6*e.gridUnit}px;
  &.mb-0 {
    margin-bottom: 0;
  }
  &.mb-8 {
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }

  .control-label {
    color: ${({theme:e})=>e.colors.grayscale.dark1};
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }

  &.extra-container {
    padding-top: 8px;
  }

  .input-container {
    display: flex;
    align-items: top;

    label {
      display: flex;
      margin-left: ${({theme:e})=>2*e.gridUnit}px;
      margin-top: ${({theme:e})=>.75*e.gridUnit}px;
      font-family: ${({theme:e})=>e.typography.families.sansSerif};
      font-size: ${({theme:e})=>e.typography.sizes.m}px;
    }

    i {
      margin: 0 ${({theme:e})=>e.gridUnit}px;
    }
  }

  input,
  textarea {
    flex: 1 1 auto;
  }

  textarea {
    height: 160px;
    resize: none;
  }

  input::placeholder,
  textarea::placeholder {
    color: ${({theme:e})=>e.colors.grayscale.light1};
  }

  textarea,
  input[type='text'],
  input[type='number'] {
    padding: ${({theme:e})=>1.5*e.gridUnit}px
      ${({theme:e})=>2*e.gridUnit}px;
    border-style: none;
    border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    border-radius: ${({theme:e})=>e.gridUnit}px;

    &[name='name'] {
      flex: 0 1 auto;
      width: 40%;
    }
  }
  &.expandable {
    height: 0;
    overflow: hidden;
    transition: height 0.25s;
    margin-left: ${({theme:e})=>8*e.gridUnit}px;
    margin-bottom: 0;
    padding: 0;
    .control-label {
      margin-bottom: 0;
    }
    &.open {
      height: ${102}px;
      padding-right: ${({theme:e})=>5*e.gridUnit}px;
    }
  }
`,P=(0,o.iK)(n.Ad)`
  flex: 1 1 auto;
  border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
  border-radius: ${({theme:e})=>e.gridUnit}px;
`,U=o.iK.div`
  padding-top: ${({theme:e})=>e.gridUnit}px;
  .input-container {
    padding-top: ${({theme:e})=>e.gridUnit}px;
    padding-bottom: ${({theme:e})=>e.gridUnit}px;
  }
  &.expandable {
    height: 0;
    overflow: hidden;
    transition: height 0.25s;
    margin-left: ${({theme:e})=>7*e.gridUnit}px;
    &.open {
      height: ${255}px;
      &.ctas-open {
        height: ${357}px;
      }
    }
  }
`,S=o.iK.div`
  padding: 0 ${({theme:e})=>4*e.gridUnit}px;
  margin-top: ${({theme:e})=>6*e.gridUnit}px;
`,L=e=>r.iv`
  font-weight: 400;
  text-transform: initial;
  padding-right: ${2*e.gridUnit}px;
`,M=e=>r.iv`
  font-weight: 400;
  text-transform: initial;
  padding: ${8*e.gridUnit}px 0 0;
  margin-left: 0px;
`,E=o.iK.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0px;

  .helper {
    color: ${({theme:e})=>e.colors.grayscale.base};
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
    margin: 0px;
  }
`,N=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
  font-weight: bold;
  font-size: ${({theme:e})=>e.typography.sizes.m}px;
`,R=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark1};
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
`,H=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.light1};
  font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
  text-transform: uppercase;
`,j=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark1};
  font-size: ${({theme:e})=>e.typography.sizes.l}px;
  font-weight: bold;
`,$=o.iK.div`
  .catalog-type-select {
    margin: 0 0 20px;
  }

  .label-select {
    text-transform: uppercase;
    color: ${({theme:e})=>e.colors.grayscale.dark1};
    font-size: 11px;
    margin: 0 5px ${({theme:e})=>2*e.gridUnit}px;
  }

  .label-paste {
    color: ${({theme:e})=>e.colors.grayscale.light1};
    font-size: 11px;
    line-height: 16px;
  }

  .input-container {
    margin: ${({theme:e})=>7*e.gridUnit}px 0;
    display: flex;
    flex-direction: column;
}
  }
  .input-form {
    height: 100px;
    width: 100%;
    border: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    border-radius: ${({theme:e})=>e.gridUnit}px;
    resize: vertical;
    padding: ${({theme:e})=>1.5*e.gridUnit}px
      ${({theme:e})=>2*e.gridUnit}px;
    &::placeholder {
      color: ${({theme:e})=>e.colors.grayscale.light1};
    }
  }

  .input-container {
    .input-upload {
      display: none;
    }
    .input-upload-current {
      display: flex;
      justify-content: space-between;
    }
    .input-upload-btn {
      width: ${({theme:e})=>32*e.gridUnit}px
    }
  }`,T=o.iK.div`
  .preferred {
    .superset-button {
      margin-left: 0;
    }
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin: ${({theme:e})=>4*e.gridUnit}px;
  }

  .preferred-item {
    width: 32%;
    margin-bottom: ${({theme:e})=>2.5*e.gridUnit}px;
  }

  .available {
    margin: ${({theme:e})=>4*e.gridUnit}px;
    .available-label {
      font-size: ${({theme:e})=>1.1*e.typography.sizes.l}px;
      font-weight: bold;
      margin: ${({theme:e})=>6*e.gridUnit}px 0;
    }
    .available-select {
      width: 100%;
    }
  }

  .label-available-select {
    text-transform: uppercase;
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
  }

  .control-label {
    color: ${({theme:e})=>e.colors.grayscale.dark1};
    font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }
`,A=(0,o.iK)(l.Z)`
  width: ${({theme:e})=>40*e.gridUnit}px;
`,k=o.iK.div`
  position: sticky;
  top: 0;
  z-index: ${({theme:e})=>e.zIndex.max};
  background: ${({theme:e})=>e.colors.grayscale.light5};
`,O=o.iK.div`
  margin-bottom: 16px;

  .catalog-type-select {
    margin: 0 0 20px;
  }

  .gsheet-title {
    font-size: ${({theme:e})=>1.1*e.typography.sizes.l}px;
    font-weight: bold;
    margin: ${({theme:e})=>10*e.gridUnit}px 0 16px;
  }

  .catalog-label {
    margin: 0 0 7px;
  }

  .catalog-name {
    display: flex;
    .catalog-name-input {
      width: 95%;
      margin-bottom: 0px;
    }
  }

  .catalog-name-url {
    margin: 4px 0;
    width: 95%;
  }

  .catalog-delete {
    align-self: center;
    background: ${({theme:e})=>e.colors.grayscale.light4};
    margin: 5px 5px 8px 5px;
  }

  .catalog-add-btn {
    width: 95%;
  }
`;var G,I;(G="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(G.register(102,"CTAS_CVAS_SCHEMA_FORM_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(255,"EXPOSE_IN_SQLLAB_FORM_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(357,"EXPOSE_ALL_FORM_HEIGHT","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(12,"anticonHeight","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(i,"no_margin_bottom","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(d,"labelMarginBotton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register((e=>r.iv`
  margin-bottom: ${4*e.gridUnit}px;
`),"marginBottom","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(c,"StyledFormHeader","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(u,"antdCollapseStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(p,"antDTabsStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(m,"antDModalNoPaddingStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(h,"infoTooltip","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(g,"toggleStyle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(b,"formScrollableStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(v,"antDModalStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(f,"antDAlertStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(y,"StyledAlertMargin","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(x,"antDErrorAlertStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(C,"formHelperStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(Z,"wideButton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(_,"formStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(w,"validatedFormStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(D,"StyledInputContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(P,"StyledJsonEditor","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(U,"StyledExpandableForm","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(S,"StyledAlignment","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(L,"buttonLinkStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(M,"alchemyButtonLinkStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(E,"TabHeader","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(N,"CreateHeaderTitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(R,"CreateHeaderSubtitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(H,"EditHeaderTitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(j,"EditHeaderSubtitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register($,"CredentialInfoForm","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(T,"SelectDatabaseStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(A,"StyledFooterButton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(k,"StyledStickyHeader","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts"),G.register(O,"StyledCatalogTable","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/DatabaseModal/styles.ts")),(I="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&I(e)},301483:(e,t,a)=>{a.d(t,{c:()=>l});var s,r,o,n=a(137703);function l(){return(0,n.v9)((e=>{var t;return null==e||null==(t=e.common)?void 0:t.conf}))}e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),("undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e})(l,"useSelector{}",(()=>[n.v9])),(r="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&r.register(l,"useCommonConf","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/state.ts"),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&o(e)},163727:(e,t,a)=>{var s,r,o,n;a.d(t,{j:()=>r}),e=a.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature,function(e){e.SQLALCHEMY_URI="sqlalchemy_form",e.DYNAMIC_FORM="dynamic_form"}(r||(r={})),(o="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&o.register(r,"CONFIGURATION_METHOD","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/database/types.ts"),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)}}]);