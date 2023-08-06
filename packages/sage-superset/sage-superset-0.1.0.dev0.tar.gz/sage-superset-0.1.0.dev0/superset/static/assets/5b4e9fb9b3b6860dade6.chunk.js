"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[859],{849576:(e,t,r)=>{r.d(t,{Z:()=>h});var a,o=r(667294),s=r(751995),n=r(87693),l=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var i="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const d=s.iK.label`
  cursor: pointer;
  display: inline-block;
  margin-bottom: 0;
`,c=(0,s.iK)(n.Z.CheckboxHalf)`
  color: ${({theme:e})=>e.colors.primary.base};
  cursor: pointer;
`,u=(0,s.iK)(n.Z.CheckboxOff)`
  color: ${({theme:e})=>e.colors.grayscale.base};
  cursor: pointer;
`,p=(0,s.iK)(n.Z.CheckboxOn)`
  color: ${({theme:e})=>e.colors.primary.base};
  cursor: pointer;
`,_=s.iK.input`
  &[type='checkbox'] {
    cursor: pointer;
    opacity: 0;
    position: absolute;
    left: 3px;
    margin: 0;
    top: 4px;
  }
`,g=s.iK.div`
  cursor: pointer;
  display: inline-block;
  position: relative;
`,m=(0,o.forwardRef)(i((({indeterminate:e,id:t,checked:r,onChange:a,title:s="",labelText:n=""},i)=>{const m=(0,o.useRef)(),f=i||m;return(0,o.useEffect)((()=>{f.current.indeterminate=e}),[f,e]),(0,l.tZ)(o.Fragment,null,(0,l.tZ)(g,null,e&&(0,l.tZ)(c,null),!e&&r&&(0,l.tZ)(p,null),!e&&!r&&(0,l.tZ)(u,null),(0,l.tZ)(_,{name:t,id:t,type:"checkbox",ref:f,checked:r,onChange:a})),(0,l.tZ)(d,{title:s,htmlFor:t},n))}),"useRef{defaultRef}\nuseEffect{}")),f=m,h=f;var v,b;(v="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(v.register(d,"CheckboxLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(c,"CheckboxHalf","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(u,"CheckboxOff","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(p,"CheckboxOn","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(_,"HiddenInput","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(g,"InputContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(m,"IndeterminateCheckbox","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx"),v.register(f,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/IndeterminateCheckbox/index.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},958237:(e,t,r)=>{r.d(t,{Z:()=>c}),r(667294);var a,o=r(751995),s=r(294184),n=r.n(s),l=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const i=o.iK.div`
  ${({theme:e,showThumbnails:t})=>`\n    display: grid;\n    grid-gap: ${12*e.gridUnit}px ${4*e.gridUnit}px;\n    grid-template-columns: repeat(auto-fit, 300px);\n    margin-top: ${-6*e.gridUnit}px;\n    padding: ${t?`${8*e.gridUnit+3}px ${9*e.gridUnit}px`:`${8*e.gridUnit+1}px ${9*e.gridUnit}px`};\n  `}
`,d=o.iK.div`
  border: 2px solid transparent;
  &.card-selected {
    border: 2px solid ${({theme:e})=>e.colors.primary.base};
  }
  &.bulk-select {
    cursor: pointer;
  }
`;function c({bulkSelectEnabled:e,loading:t,prepareRow:r,renderCard:a,rows:o,showThumbnails:s}){return a?(0,l.tZ)(i,{showThumbnails:s},t&&0===o.length&&[...new Array(25)].map(((e,r)=>(0,l.tZ)("div",{key:r},a({loading:t})))),o.length>0&&o.map((o=>a?(r(o),(0,l.tZ)(d,{className:n()({"card-selected":e&&o.isSelected,"bulk-select":e}),key:o.id,onClick:t=>{return r=t,a=o.toggleRowSelected,void(e&&(r.preventDefault(),r.stopPropagation(),a()));var r,a},role:"none"},a({...o.original,loading:t}))):null))):null}var u,p;(u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(u.register(i,"CardContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/CardCollection.tsx"),u.register(d,"CardWrapper","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/CardCollection.tsx"),u.register(c,"CardCollection","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/CardCollection.tsx")),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&p(e)},824129:(e,t,r)=>{r.d(t,{s:()=>_});var a,o=r(667294),s=r(751995),n=r(455867),l=r(104715),i=r(558347),d=r(800062),c=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const p=s.iK.div`
  display: inline-flex;
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
  align-items: center;
  text-align: left;
  width: ${d.Lh}px;
`,_=({initialSort:e,onChange:t,options:r,pageIndex:a,pageSize:s})=>{const d=e&&r.find((({id:t})=>t===e[0].id))||r[0],[u,_]=(0,o.useState)({label:d.label,value:d.value}),g=(0,o.useMemo)((()=>r.map((e=>({label:e.label,value:e.value})))),[r]);return(0,c.tZ)(p,null,(0,c.tZ)(l.P,{ariaLabel:(0,n.t)("Sort"),header:(0,c.tZ)(i.lX,null,(0,n.t)("Sort")),labelInValue:!0,onChange:e=>(e=>{_(e);const o=r.find((({value:t})=>t===e.value));if(o){const e=[{id:o.id,desc:o.desc}];t({pageIndex:a,pageSize:s,sortBy:e,filters:[]})}})(e),options:g,showSearch:!0,value:u}))};var g,m;u(_,"useState{[value, setValue]({\n        label: defaultSort.label,\n        value: defaultSort.value,\n    })}\nuseMemo{formattedOptions}"),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(g.register(p,"SortContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/CardSortSelect.tsx"),g.register(_,"CardSortSelect","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/CardSortSelect.tsx")),(m="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&m(e)},471801:(e,t,r)=>{r.d(t,{G:()=>n});var a,o=r(751995),s=r(800062);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const n=o.iK.div`
  display: inline-flex;
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
  align-items: center;
  width: ${s.Lh}px;
`;var l,i;(l="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&l.register(n,"FilterContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Base.ts"),(i="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&i(e)},767975:(e,t,r)=>{r.d(t,{Z:()=>_});var a,o=r(667294),s=r(730381),n=r.n(s),l=r(751995),i=r(662276),d=r(558347),c=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var u="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const p=l.iK.div`
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  width: 360px;
`;function _({Header:e,initialValue:t,onSubmit:r}){const[a,s]=(0,o.useState)(null!=t?t:null),l=(0,o.useMemo)((()=>!a||Array.isArray(a)&&!a.length?null:[n()(a[0]),n()(a[1])]),[a]);return(0,c.tZ)(p,null,(0,c.tZ)(d.lX,null,e),(0,c.tZ)(i.S,{showTime:!0,value:l,onChange:e=>{var t,a,o,n;if(!e)return s(null),void r([]);const l=[null!=(t=null==(a=e[0])?void 0:a.valueOf())?t:0,null!=(o=null==(n=e[1])?void 0:n.valueOf())?o:0];s(l),r(l)}}))}var g,m;u(_,"useState{[value, setValue](initialValue ?? null)}\nuseMemo{momentValue}"),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(g.register(p,"RangeFilterContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/DateRange.tsx"),g.register(_,"DateRangeFilter","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/DateRange.tsx")),(m="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&m(e)},120447:(e,t,r)=>{r.d(t,{Z:()=>f}),r(115306);var a,o=r(667294),s=r(751995),n=r(455867),l=r(87693),i=r(582191),d=r(800062),c=r(558347),u=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const _=s.iK.div`
  width: ${d.Lh}px;
`,g=(0,s.iK)(l.Z.Search)`
  color: ${({theme:e})=>e.colors.grayscale.light1};
`,m=(0,s.iK)(i.oc)`
  border-radius: ${({theme:e})=>e.gridUnit}px;
`;function f({Header:e,name:t,initialValue:r,onSubmit:a}){const[s,l]=(0,o.useState)(r||""),i=()=>{s&&a(s.trim().replace(/\+/g,"%2B"))};return(0,u.tZ)(_,null,(0,u.tZ)(c.lX,null,e),(0,u.tZ)(m,{allowClear:!0,"data-test":"filters-search",placeholder:(0,n.t)("Type a value"),name:t,value:s,onChange:e=>{l(e.currentTarget.value),""===e.currentTarget.value&&a("")},onPressEnter:i,onBlur:i,prefix:(0,u.tZ)(g,{iconSize:"l"})}))}var h,v;p(f,"useState{[value, setValue](initialValue || '')}"),(h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(h.register(_,"Container","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Search.tsx"),h.register(g,"SearchIcon","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Search.tsx"),h.register(m,"StyledInput","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Search.tsx"),h.register(f,"SearchFilter","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Search.tsx")),(v="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&v(e)},994081:(e,t,r)=>{r.d(t,{Z:()=>p});var a,o=r(667294),s=r(455867),n=r(104715),l=r(558347),i=r(471801),d=r(211965);function c({Header:e,name:t,fetchSelects:r,initialValue:a,onSelect:c,selects:u=[]}){const[p,_]=(0,o.useState)(a),g=(0,o.useMemo)((()=>async(e,t,a)=>{if(r){const o=await r(e,t,a);return{data:o.data,totalCount:o.totalCount}}return{data:[],totalCount:0}}),[r]);return(0,d.tZ)(i.G,null,(0,d.tZ)(n.P,{allowClear:!0,ariaLabel:"string"==typeof e?e:t||(0,s.t)("Filter"),labelInValue:!0,"data-test":"filters-select",header:(0,d.tZ)(l.lX,null,e),onChange:e=>{c(e?{label:e.label,value:e.value}:void 0),_(e)},onClear:()=>{c(void 0),_(void 0)},options:r?g:u,placeholder:(0,s.t)("Select or type a value"),showSearch:!0,value:p}))}e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),("undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e})(c,"useState{[selectedOption, setSelectedOption](initialValue)}\nuseMemo{fetchAndFormatSelects}");const u=c,p=u;var _,g;(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(_.register(c,"SelectFilter","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Select.tsx"),_.register(u,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/Select.tsx")),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&g(e)},152416:(e,t,r)=>{r.d(t,{Z:()=>p});var a,o=r(667294),s=r(468135),n=r(120447),l=r(994081),i=r(767975),d=r(211965);function c({filters:e,internalFilters:t=[],updateFilterValue:r}){return(0,d.tZ)(o.Fragment,null,e.map((({Header:e,fetchSelects:a,id:o,input:s,paginate:c,selects:u},p)=>{const _=t[p]&&t[p].value;return"select"===s?(0,d.tZ)(l.Z,{Header:e,fetchSelects:a,initialValue:_,key:o,name:o,onSelect:e=>r(p,e),paginate:c,selects:u}):"search"===s&&"string"==typeof e?(0,d.tZ)(n.Z,{Header:e,initialValue:_,key:o,name:o,onSubmit:e=>r(p,e)}):"datetime_range"===s?(0,d.tZ)(i.Z,{Header:e,initialValue:_,key:o,name:o,onSubmit:e=>r(p,e)}):null})))}e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const u=(0,s.b)(c),p=u;var _,g;(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(_.register(c,"UIFilters","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/index.tsx"),_.register(u,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/Filters/index.tsx")),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&g(e)},112142:(e,t,r)=>{r.d(t,{Z:()=>Z});var a,o,s=r(205872),n=r.n(s),l=r(751995),i=r(455867),d=r(667294),c=r(582191),u=r(229487);function p(){return p=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var a in r)Object.prototype.hasOwnProperty.call(r,a)&&(e[a]=r[a])}return e},p.apply(this,arguments)}const _=function(e){return d.createElement("svg",p({width:119,height:76,viewBox:"0 0 119 76",fill:"none",xmlns:"http://www.w3.org/2000/svg"},e),a||(a=d.createElement("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M83.195 1.366L103 24v38a4 4 0 01-4 4H20a4 4 0 01-4-4V24L35.805 1.366A4 4 0 0138.815 0h41.37a4 4 0 013.01 1.366zM101 26v36a2 2 0 01-2 2H20a2 2 0 01-2-2V26h17.25A4.75 4.75 0 0140 30.75a6.75 6.75 0 006.75 6.75h25.5A6.75 6.75 0 0079 30.75 4.75 4.75 0 0183.75 26H101zm-.658-2L81.69 2.683A2 2 0 0080.185 2h-41.37a2 2 0 00-1.505.683L18.657 24H35.25A6.75 6.75 0 0142 30.75a4.75 4.75 0 004.75 4.75h25.5A4.75 4.75 0 0077 30.75 6.75 6.75 0 0183.75 24h16.592z",fill:"#D1D1D1"})),o||(o=d.createElement("path",{d:"M16 53.29C6.074 55.7 0 58.94 0 62.5 0 69.956 26.64 76 59.5 76S119 69.956 119 62.5c0-3.56-6.074-6.799-16-9.21V62a4 4 0 01-4 4H20a4 4 0 01-4-4v-8.71z",fill:"#F2F2F2"})))};var g,m=r(294184),f=r.n(m),h=r(835932),v=r(87693),b=r(849576),L=r(212591),y=r(397754),P=r(958237),w=r(152416),x=r(824129),E=r(800062),M=r(211965);e=r.hmd(e),(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&g(e);var C="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const H=l.iK.div`
  text-align: center;

  .superset-list-view {
    text-align: left;
    border-radius: 4px 0;
    margin: 0 ${({theme:e})=>4*e.gridUnit}px;

    .header {
      display: flex;
      padding-bottom: ${({theme:e})=>4*e.gridUnit}px;

      & .controls {
        display: flex;
        flex-wrap: wrap;
        column-gap: ${({theme:e})=>6*e.gridUnit}px;
        row-gap: ${({theme:e})=>4*e.gridUnit}px;
      }
    }

    .body.empty table {
      margin-bottom: 0;
    }

    .body {
      overflow-x: auto;
    }

    .ant-empty {
      .ant-empty-image {
        height: auto;
      }
    }
  }

  .pagination-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: ${({theme:e})=>4*e.gridUnit}px;
  }

  .row-count-container {
    margin-top: ${({theme:e})=>2*e.gridUnit}px;
    color: ${({theme:e})=>e.colors.grayscale.base};
  }
`,S=(0,l.iK)(u.Z)`
  border-radius: 0;
  margin-bottom: 0;
  color: #3d3d3d;
  background-color: ${({theme:e})=>e.colors.primary.light4};

  .selectedCopy {
    display: inline-block;
    padding: ${({theme:e})=>2*e.gridUnit}px 0;
  }

  .deselect-all {
    color: #1985a0;
    margin-left: ${({theme:e})=>4*e.gridUnit}px;
  }

  .divider {
    margin: ${({theme:{gridUnit:e}})=>`${2*-e}px 0 ${2*-e}px ${4*e}px`};
    width: 1px;
    height: ${({theme:e})=>8*e.gridUnit}px;
    box-shadow: inset -1px 0px 0px #dadada;
    display: inline-flex;
    vertical-align: middle;
    position: relative;
  }

  .ant-alert-close-icon {
    margin-top: ${({theme:e})=>1.5*e.gridUnit}px;
  }
`,U={Cell:({row:e})=>(0,M.tZ)(b.Z,n()({},e.getToggleRowSelectedProps(),{id:e.id})),Header:({getToggleAllRowsSelectedProps:e})=>(0,M.tZ)(b.Z,n()({},e(),{id:"header-toggle-all"})),id:"selection",size:"sm"},V=l.iK.div`
  padding-right: ${({theme:e})=>4*e.gridUnit}px;
  margin-top: ${({theme:e})=>5*e.gridUnit+1}px;
  white-space: nowrap;
  display: inline-block;

  .toggle-button {
    display: inline-block;
    border-radius: ${({theme:e})=>e.gridUnit/2}px;
    padding: ${({theme:e})=>e.gridUnit}px;
    padding-bottom: ${({theme:e})=>.5*e.gridUnit}px;

    &:first-of-type {
      margin-right: ${({theme:e})=>2*e.gridUnit}px;
    }
  }

  .active {
    background-color: ${({theme:e})=>e.colors.grayscale.base};
    svg {
      color: ${({theme:e})=>e.colors.grayscale.light5};
    }
  }
`,G=l.iK.div`
  padding: ${({theme:e})=>40*e.gridUnit}px 0;

  &.table {
    background: ${({theme:e})=>e.colors.grayscale.light5};
  }
`,O=({mode:e,setMode:t})=>(0,M.tZ)(V,null,(0,M.tZ)("div",{role:"button",tabIndex:0,onClick:e=>{e.currentTarget.blur(),t("card")},className:f()("toggle-button",{active:"card"===e})},(0,M.tZ)(v.Z.CardView,null)),(0,M.tZ)("div",{role:"button",tabIndex:0,onClick:e=>{e.currentTarget.blur(),t("table")},className:f()("toggle-button",{active:"table"===e})},(0,M.tZ)(v.Z.ListView,null)));function D({columns:e,data:t,count:r,pageSize:a,fetchData:o,loading:s,initialSort:n=[],className:l="",filters:u=[],bulkActions:p=[],bulkSelectEnabled:g=!1,disableBulkSelect:m=(()=>{}),renderBulkSelectCopy:f=(e=>(0,i.t)("%s Selected",e.length)),renderCard:v,showThumbnails:b,cardSortSelectOptions:C,defaultViewMode:V="card",highlightRowId:D,emptyState:I={}}){const{getTableProps:Z,getTableBodyProps:k,headerGroups:T,rows:R,prepareRow:F,pageCount:B=1,gotoPage:A,applyFilterValue:K,selectedFlatRows:j,toggleAllRowsSelected:W,setViewMode:$,state:{pageIndex:q,pageSize:z,internalFilters:N,viewMode:Q}}=(0,E.o4)({bulkSelectColumnConfig:U,bulkSelectMode:g&&Boolean(p.length),columns:e,count:r,data:t,fetchData:o,initialPageSize:a,initialSort:n,initialFilters:u,renderCard:Boolean(v),defaultViewMode:V}),X=Boolean(u.length);if(X){const t=e.reduce(((e,t)=>({...e,[t.id||t.accessor]:!0})),{});u.forEach((e=>{if(!t[e.id])throw new E.QG(`Invalid filter config, ${e.id} is not present in columns`)}))}const Y=Boolean(v);return(0,d.useEffect)((()=>{g||W(!1)}),[g,W]),(0,M.tZ)(H,null,(0,M.tZ)("div",{"data-test":l,className:`superset-list-view ${l}`},(0,M.tZ)("div",{className:"header"},Y&&(0,M.tZ)(O,{mode:Q,setMode:$}),(0,M.tZ)("div",{className:"controls"},X&&(0,M.tZ)(w.Z,{filters:u,internalFilters:N,updateFilterValue:K}),"card"===Q&&C&&(0,M.tZ)(x.s,{initialSort:n,onChange:o,options:C,pageIndex:q,pageSize:z}))),(0,M.tZ)("div",{className:"body "+(0===R.length?"empty":"")},g&&(0,M.tZ)(S,{"data-test":"bulk-select-controls",type:"info",closable:!0,showIcon:!1,onClose:m,message:(0,M.tZ)(d.Fragment,null,(0,M.tZ)("div",{className:"selectedCopy","data-test":"bulk-select-copy"},f(j)),Boolean(j.length)&&(0,M.tZ)(d.Fragment,null,(0,M.tZ)("span",{"data-test":"bulk-select-deselect-all",role:"button",tabIndex:0,className:"deselect-all",onClick:()=>W(!1)},(0,i.t)("Deselect all")),(0,M.tZ)("div",{className:"divider"}),p.map((e=>(0,M.tZ)(h.Z,{"data-test":"bulk-select-action",key:e.key,buttonStyle:e.type,cta:!0,onClick:()=>e.onSelect(j.map((e=>e.original)))},e.name)))))}),"card"===Q&&(0,M.tZ)(P.Z,{bulkSelectEnabled:g,prepareRow:F,renderCard:v,rows:R,loading:s,showThumbnails:b}),"table"===Q&&(0,M.tZ)(y.Z,{getTableProps:Z,getTableBodyProps:k,prepareRow:F,headerGroups:T,rows:R,columns:e,loading:s,highlightRowId:D}),!s&&0===R.length&&(0,M.tZ)(G,{className:Q},(0,M.tZ)(c.HY,{image:(0,M.tZ)(_,null),description:I.message||(0,i.t)("No Data")},I.slot||null)))),R.length>0&&(0,M.tZ)("div",{className:"pagination-container"},(0,M.tZ)(L.Z,{totalPages:B||0,currentPage:B?q+1:0,onChange:e=>A(e-1),hideFirstAndLastPageLinks:!0}),(0,M.tZ)("div",{className:"row-count-container"},!s&&(0,i.t)("%s-%s of %s",z*q+(R.length&&1),z*q+R.length,r))))}C(D,"useListViewState{{ getTableProps, getTableBodyProps, headerGroups, rows, prepareRow, pageCount = 1, gotoPage, applyFilterValue, selectedFlatRows, toggleAllRowsSelected, setViewMode, state: { pageIndex, pageSize, internalFilters, viewMode }, }}\nuseEffect{}",(()=>[E.o4]));const I=D,Z=I;var k,T;(k="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(k.register(H,"ListViewStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(S,"BulkSelectWrapper","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(U,"bulkSelectColumnConfig","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(V,"ViewModeContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(G,"EmptyWrapper","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(O,"ViewModeToggle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(D,"ListView","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx"),k.register(I,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ListView.tsx")),(T="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&T(e)},550859:(e,t,r)=>{r.d(t,{p:()=>o.p,Z:()=>a.Z});var a=r(112142),o=r(349111);"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature},349111:(e,t,r)=>{var a,o,s,n;r.d(t,{p:()=>o}),e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature,function(e){e.startsWith="sw",e.endsWith="ew",e.contains="ct",e.equals="eq",e.notStartsWith="nsw",e.notEndsWith="new",e.notContains="nct",e.notEquals="neq",e.greaterThan="gt",e.lessThan="lt",e.relationManyMany="rel_m_m",e.relationOneMany="rel_o_m",e.titleOrSlug="title_or_slug",e.nameOrDescription="name_or_description",e.allText="all_text",e.chartAllText="chart_all_text",e.datasetIsNullOrEmpty="dataset_is_null_or_empty",e.between="between",e.dashboardIsFav="dashboard_is_favorite",e.chartIsFav="chart_is_favorite",e.chartIsCertified="chart_is_certified",e.dashboardIsCertified="dashboard_is_certified"}(o||(o={})),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&s.register(o,"FilterOperator","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/types.ts"),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&n(e)},800062:(module,__webpack_exports__,__webpack_require__)=>{__webpack_require__.d(__webpack_exports__,{Lh:()=>SELECT_WIDTH,QG:()=>ListViewError,o4:()=>useListViewState});var lodash_isEqual__WEBPACK_IMPORTED_MODULE_0__=__webpack_require__(618446),lodash_isEqual__WEBPACK_IMPORTED_MODULE_0___default=__webpack_require__.n(lodash_isEqual__WEBPACK_IMPORTED_MODULE_0__),core_js_modules_es_string_replace_js__WEBPACK_IMPORTED_MODULE_1__=__webpack_require__(115306),core_js_modules_es_string_replace_js__WEBPACK_IMPORTED_MODULE_1___default=__webpack_require__.n(core_js_modules_es_string_replace_js__WEBPACK_IMPORTED_MODULE_1__),react__WEBPACK_IMPORTED_MODULE_2__=__webpack_require__(667294),react_table__WEBPACK_IMPORTED_MODULE_3__=__webpack_require__(379521),react_table__WEBPACK_IMPORTED_MODULE_3___default=__webpack_require__.n(react_table__WEBPACK_IMPORTED_MODULE_3__),use_query_params__WEBPACK_IMPORTED_MODULE_4__=__webpack_require__(535755),rison__WEBPACK_IMPORTED_MODULE_5__=__webpack_require__(115926),rison__WEBPACK_IMPORTED_MODULE_5___default=__webpack_require__.n(rison__WEBPACK_IMPORTED_MODULE_5__),enterModule;module=__webpack_require__.hmd(module),enterModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0,enterModule&&enterModule(module);var __signature__="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const RisonParam={encode:e=>void 0===e?void 0:rison__WEBPACK_IMPORTED_MODULE_5___default().encode(e).replace(/\+/g,"%2B"),decode:e=>void 0===e||Array.isArray(e)?void 0:rison__WEBPACK_IMPORTED_MODULE_5___default().decode(e)},SELECT_WIDTH=200;class ListViewError extends Error{constructor(...e){super(...e),this.name="ListViewError"}__reactstandin__regenerateByEval(key,code){this[key]=eval(code)}}function removeFromList(e,t){return e.filter(((e,r)=>t!==r))}function updateInList(e,t,r){const a=e.find(((e,r)=>t===r));return[...e.slice(0,t),{...a,...r},...e.slice(t+1)]}function mergeCreateFilterValues(e,t){return e.map((({id:e,urlDisplay:r,operator:a})=>({id:e,urlDisplay:r,operator:a,value:t[r||e]})))}function convertFilters(e){return e.filter((e=>!(void 0===e.value||Array.isArray(e.value)&&!e.value.length))).map((({value:e,operator:t,id:r})=>"between"===t&&Array.isArray(e)?[{value:e[0],operator:"gt",id:r},{value:e[1],operator:"lt",id:r}]:{value:e,operator:t,id:r})).flat()}function convertFiltersRison(e,t){const r=[],a={};return Object.keys(e).forEach((t=>{const o={id:t,value:e[t]};a[t]=o,r.push(o)})),t.forEach((e=>{const t=e.urlDisplay||e.id,r=a[t];r&&(r.operator=e.operator,r.id=e.id)})),r}function extractInputValue(e,t){return e&&"text"!==e?"checkbox"===e?t.currentTarget.checked:null:t.currentTarget.value}function useListViewState({fetchData:e,columns:t,data:r,count:a,initialPageSize:o,initialFilters:s=[],initialSort:n=[],bulkSelectMode:l=!1,bulkSelectColumnConfig:i,renderCard:d=!1,defaultViewMode:c="card"}){const[u,p]=(0,use_query_params__WEBPACK_IMPORTED_MODULE_4__.Kx)({filters:RisonParam,pageIndex:use_query_params__WEBPACK_IMPORTED_MODULE_4__.yz,sortColumn:use_query_params__WEBPACK_IMPORTED_MODULE_4__.Zp,sortOrder:use_query_params__WEBPACK_IMPORTED_MODULE_4__.Zp,viewMode:use_query_params__WEBPACK_IMPORTED_MODULE_4__.Zp}),_=(0,react__WEBPACK_IMPORTED_MODULE_2__.useMemo)((()=>u.sortColumn&&u.sortOrder?[{id:u.sortColumn,desc:"desc"===u.sortOrder}]:n),[u.sortColumn,u.sortOrder]),g={filters:u.filters?convertFiltersRison(u.filters,s):[],pageIndex:u.pageIndex||0,pageSize:o,sortBy:_},[m,f]=(0,react__WEBPACK_IMPORTED_MODULE_2__.useState)(u.viewMode||(d?c:"table")),h=(0,react__WEBPACK_IMPORTED_MODULE_2__.useMemo)((()=>{const e=t.map((e=>({...e,filter:"exact"})));return l?[i,...e]:e}),[l,t]),{getTableProps:v,getTableBodyProps:b,headerGroups:L,rows:y,prepareRow:P,canPreviousPage:w,canNextPage:x,pageCount:E,gotoPage:M,setAllFilters:C,selectedFlatRows:H,toggleAllRowsSelected:S,state:{pageIndex:U,pageSize:V,sortBy:G,filters:O}}=(0,react_table__WEBPACK_IMPORTED_MODULE_3__.useTable)({columns:h,count:a,data:r,disableFilters:!0,disableSortRemove:!0,initialState:g,manualFilters:!0,manualPagination:!0,manualSortBy:!0,autoResetFilters:!1,pageCount:Math.ceil(a/o)},react_table__WEBPACK_IMPORTED_MODULE_3__.useFilters,react_table__WEBPACK_IMPORTED_MODULE_3__.useSortBy,react_table__WEBPACK_IMPORTED_MODULE_3__.usePagination,react_table__WEBPACK_IMPORTED_MODULE_3__.useRowState,react_table__WEBPACK_IMPORTED_MODULE_3__.useRowSelect),[D,I]=(0,react__WEBPACK_IMPORTED_MODULE_2__.useState)(u.filters&&s.length?mergeCreateFilterValues(s,u.filters):[]);return(0,react__WEBPACK_IMPORTED_MODULE_2__.useEffect)((()=>{s.length&&I(mergeCreateFilterValues(s,u.filters?u.filters:{}))}),[s]),(0,react__WEBPACK_IMPORTED_MODULE_2__.useEffect)((()=>{const t={};D.forEach((e=>{if(void 0!==e.value&&("string"!=typeof e.value||e.value.length>0)){const r=e.urlDisplay||e.id;t[r]=e.value}}));const r={filters:Object.keys(t).length?t:void 0,pageIndex:U};G[0]&&(r.sortColumn=G[0].id,r.sortOrder=G[0].desc?"desc":"asc"),d&&(r.viewMode=m);const a=void 0!==u.pageIndex&&r.pageIndex!==u.pageIndex?"push":"replace";p(r,a),e({pageIndex:U,pageSize:V,sortBy:G,filters:O})}),[e,U,V,G,O]),(0,react__WEBPACK_IMPORTED_MODULE_2__.useEffect)((()=>{lodash_isEqual__WEBPACK_IMPORTED_MODULE_0___default()(g.pageIndex,U)||M(g.pageIndex)}),[u]),{canNextPage:x,canPreviousPage:w,getTableBodyProps:b,getTableProps:v,gotoPage:M,headerGroups:L,pageCount:E,prepareRow:P,rows:y,selectedFlatRows:H,setAllFilters:C,state:{pageIndex:U,pageSize:V,sortBy:G,filters:O,internalFilters:D,viewMode:m},toggleAllRowsSelected:S,applyFilterValue:(e,t)=>{I((r=>{if(r[e].value===t)return r;const a={...r[e],value:t},o=updateInList(r,e,a);return C(convertFilters(o)),M(0),o}))},setViewMode:f}}__signature__(useListViewState,"useQueryParams{[query, setQuery]}\nuseMemo{initialSortBy}\nuseState{[viewMode, setViewMode](query.viewMode ||\n        (renderCard ? defaultViewMode : 'table'))}\nuseMemo{columnsWithSelect}\nuseTable{{ getTableProps, getTableBodyProps, headerGroups, rows, prepareRow, canPreviousPage, canNextPage, pageCount, gotoPage, setAllFilters, selectedFlatRows, toggleAllRowsSelected, state: { pageIndex, pageSize, sortBy, filters }, }}\nuseState{[internalFilters, setInternalFilters](query.filters && initialFilters.length\n        ? mergeCreateFilterValues(initialFilters, query.filters)\n        : [])}\nuseEffect{}\nuseEffect{}\nuseEffect{}",(()=>[use_query_params__WEBPACK_IMPORTED_MODULE_4__.Kx,react_table__WEBPACK_IMPORTED_MODULE_3__.useTable]));const filterSelectStyles={container:(e,{getValue:t})=>({...e,minWidth:`${Math.min(12,Math.max(5,3+t()[0].label.length/2))}em`}),control:e=>({...e,borderWidth:0,boxShadow:"none",cursor:"pointer",backgroundColor:"transparent"})};var reactHotLoader,leaveModule;reactHotLoader="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0,reactHotLoader&&(reactHotLoader.register(RisonParam,"RisonParam","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(SELECT_WIDTH,"SELECT_WIDTH","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(ListViewError,"ListViewError","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(removeFromList,"removeFromList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(updateInList,"updateInList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(mergeCreateFilterValues,"mergeCreateFilterValues","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(convertFilters,"convertFilters","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(convertFiltersRison,"convertFiltersRison","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(extractInputValue,"extractInputValue","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(useListViewState,"useListViewState","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts"),reactHotLoader.register(filterSelectStyles,"filterSelectStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/utils.ts")),leaveModule="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0,leaveModule&&leaveModule(module)}}]);