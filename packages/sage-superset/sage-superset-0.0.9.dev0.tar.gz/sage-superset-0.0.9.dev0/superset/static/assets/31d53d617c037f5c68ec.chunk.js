"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[7633],{715073:(e,t,r)=>{r.r(t),r.d(t,{default:()=>k});var s,a=r(667294),o=r(751995),n=r(455867),i=r(431069),l=r(730381),u=r.n(l),d=r(440768),c=r(414114),p=r(34858),y=r(620755),h=r(976697),g=r(495413),m=r(550859),v=r(358593),b=r(242110),f=r(833743),w=r(600120),Z=r(427600),q=r(400012),x=r(87693),C=r(824527),P=r(211965);e=r.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e);var L="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const U=(0,o.iK)(m.Z)`
  table .table-cell {
    vertical-align: top;
  }
`;b.Z.registerLanguage("sql",f.Z);const S=(0,o.iK)(b.Z)`
  height: ${({theme:e})=>26*e.gridUnit}px;
  overflow: hidden !important; /* needed to override inline styles */
  text-overflow: ellipsis;
  white-space: nowrap;
`,H=o.iK.div`
  .count {
    margin-left: 5px;
    color: ${({theme:e})=>e.colors.primary.base};
    text-decoration: underline;
    cursor: pointer;
  }
`,Q=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
`;function $({addDangerToast:e,addSuccessToast:t}){const{state:{loading:r,resourceCount:s,resourceCollection:l},fetchData:c}=(0,p.Yi)("query",(0,n.t)("Query history"),e,!1),[b,f]=(0,a.useState)(),L=(0,o.Fg)(),$=(0,a.useCallback)((t=>{i.Z.get({endpoint:`/api/v1/query/${t}`}).then((({json:e={}})=>{f({...e.result})}),(0,d.v$)((t=>e((0,n.t)("There was an issue previewing the selected query. %s",t)))))}),[e]),D={activeChild:"Query history",...g.Y},k=[{id:q.J.start_time,desc:!0}],T=(0,a.useMemo)((()=>[{Cell:({row:{original:{status:e}}})=>{const t={name:null,label:""};return"success"===e?(t.name=(0,P.tZ)(x.Z.Check,{iconColor:L.colors.success.base}),t.label=(0,n.t)("Success")):"failed"===e||"stopped"===e?(t.name=(0,P.tZ)(x.Z.XSmall,{iconColor:"failed"===e?L.colors.error.base:L.colors.grayscale.base}),t.label=(0,n.t)("Failed")):"running"===e?(t.name=(0,P.tZ)(x.Z.Running,{iconColor:L.colors.primary.base}),t.label=(0,n.t)("Running")):"timed_out"===e?(t.name=(0,P.tZ)(x.Z.Offline,{iconColor:L.colors.grayscale.light1}),t.label=(0,n.t)("Offline")):"scheduled"!==e&&"pending"!==e||(t.name=(0,P.tZ)(x.Z.Queued,{iconColor:L.colors.grayscale.base}),t.label=(0,n.t)("Scheduled")),(0,P.tZ)(v.u,{title:t.label,placement:"bottom"},(0,P.tZ)("span",null,t.name))},accessor:q.J.status,size:"xs",disableSortBy:!0},{accessor:q.J.start_time,Header:(0,n.t)("Time"),size:"xl",Cell:({row:{original:{start_time:e,end_time:t}}})=>{const r=u().utc(e).local().format(Z.v2).split(" "),s=(0,P.tZ)(a.Fragment,null,r[0]," ",(0,P.tZ)("br",null),r[1]);return t?(0,P.tZ)(v.u,{title:(0,n.t)("Duration: %s",u()(u().utc(t-e)).format(Z.n2)),placement:"bottom"},(0,P.tZ)("span",null,s)):s}},{accessor:q.J.tab_name,Header:(0,n.t)("Tab name"),size:"xl"},{accessor:q.J.database_name,Header:(0,n.t)("Database"),size:"xl"},{accessor:q.J.database,hidden:!0},{accessor:q.J.schema,Header:(0,n.t)("Schema"),size:"xl"},{Cell:({row:{original:{sql_tables:e=[]}}})=>{const t=e.map((e=>e.table)),r=t.length>0?t.shift():"";return t.length?(0,P.tZ)(H,null,(0,P.tZ)("span",null,r),(0,P.tZ)(h.Z,{placement:"right",title:(0,n.t)("TABLES"),trigger:"click",content:(0,P.tZ)(a.Fragment,null,t.map((e=>(0,P.tZ)(Q,{key:e},e))))},(0,P.tZ)("span",{className:"count"},"(+",t.length,")"))):r},accessor:q.J.sql_tables,Header:(0,n.t)("Tables"),size:"xl",disableSortBy:!0},{accessor:q.J.user_first_name,Header:(0,n.t)("User"),size:"xl",Cell:({row:{original:{user:e}}})=>e?`${e.first_name} ${e.last_name}`:""},{accessor:q.J.user,hidden:!0},{accessor:q.J.rows,Header:(0,n.t)("Rows"),size:"md"},{accessor:q.J.sql,Header:(0,n.t)("SQL"),Cell:({row:{original:e,id:t}})=>(0,P.tZ)("div",{tabIndex:0,role:"button","data-test":`open-sql-preview-${t}`,onClick:()=>f(e)},(0,P.tZ)(S,{language:"sql",style:w.Z},(0,d.IB)(e.sql,4)))},{Header:(0,n.t)("Actions"),id:"actions",disableSortBy:!0,Cell:({row:{original:{id:e}}})=>(0,P.tZ)(v.u,{title:(0,n.t)("Open query in SQL Lab"),placement:"bottom"},(0,P.tZ)("a",{href:`/superset/sqllab?queryId=${e}`},(0,P.tZ)(x.Z.Full,{iconColor:L.colors.grayscale.base})))}]),[]),R=(0,a.useMemo)((()=>[{Header:(0,n.t)("Database"),id:"database",input:"select",operator:m.p.relationOneMany,unfilteredLabel:"All",fetchSelects:(0,d.tm)("query","database",(0,d.v$)((t=>e((0,n.t)("An error occurred while fetching database values: %s",t))))),paginate:!0},{Header:(0,n.t)("State"),id:"status",input:"select",operator:m.p.equals,unfilteredLabel:"All",fetchSelects:(0,d.wk)("query","status",(0,d.v$)((t=>e((0,n.t)("An error occurred while fetching schema values: %s",t))))),paginate:!0},{Header:(0,n.t)("User"),id:"user",input:"select",operator:m.p.relationOneMany,unfilteredLabel:"All",fetchSelects:(0,d.tm)("query","user",(0,d.v$)((t=>e((0,n.t)("An error occurred while fetching user values: %s",t))))),paginate:!0},{Header:(0,n.t)("Time range"),id:"start_time",input:"datetime_range",operator:m.p.between},{Header:(0,n.t)("Search by query text"),id:"sql",input:"search",operator:m.p.contains}]),[e]);return(0,P.tZ)(a.Fragment,null,(0,P.tZ)(y.Z,D),b&&(0,P.tZ)(C.Z,{onHide:()=>f(void 0),query:b,queries:l,fetchData:$,openInSqlLab:e=>window.location.assign(`/superset/sqllab?queryId=${e}`),show:!0}),(0,P.tZ)(U,{className:"query-history-list-view",columns:T,count:s,data:l,fetchData:c,filters:R,initialSort:k,loading:r,pageSize:25,highlightRowId:null==b?void 0:b.id}))}L($,"useListViewResource{{ state: { loading, resourceCount: queryCount, resourceCollection: queries }, fetchData, }}\nuseState{[queryCurrentlyPreviewing, setQueryCurrentlyPreviewing]}\nuseTheme{theme}\nuseCallback{handleQueryPreview}\nuseMemo{columns}\nuseMemo{filters}",(()=>[p.Yi,o.Fg]));const D=(0,c.Z)($),k=D;var T,R;(T="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(T.register(25,"PAGE_SIZE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(4,"SQL_PREVIEW_MAX_LINES","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(U,"TopAlignedListView","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(S,"StyledSyntaxHighlighter","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(H,"StyledTableLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(Q,"StyledPopoverItem","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register($,"QueryList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx"),T.register(D,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryList.tsx")),(R="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&R(e)},824527:(e,t,r)=>{r.d(t,{Z:()=>x});var s,a=r(667294),o=r(751995),n=r(455867),i=r(574520),l=r(294184),u=r.n(l),d=r(835932),c=r(414114),p=r(331673),y=r(14025),h=r(211965);e=r.hmd(e),(s="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&s(e);var g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const m=o.iK.div`
  color: ${({theme:e})=>e.colors.secondary.light2};
  font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
  margin-bottom: 0;
  text-transform: uppercase;
`,v=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
  font-size: ${({theme:e})=>e.typography.sizes.m-1}px;
  padding: 4px 0 24px 0;
`,b=o.iK.div`
  margin: 0 0 ${({theme:e})=>6*e.gridUnit}px 0;
`,f=o.iK.div`
  display: inline;
  font-size: ${({theme:e})=>e.typography.sizes.s}px;
  padding: ${({theme:e})=>2*e.gridUnit}px
    ${({theme:e})=>4*e.gridUnit}px;
  margin-right: ${({theme:e})=>4*e.gridUnit}px;
  color: ${({theme:e})=>e.colors.secondary.dark1};

  &.active,
  &:focus,
  &:hover {
    background: ${({theme:e})=>e.colors.secondary.light4};
    border-bottom: none;
    border-radius: ${({theme:e})=>e.borderRadius}px;
    margin-bottom: ${({theme:e})=>2*e.gridUnit}px;
  }

  &:hover:not(.active) {
    background: ${({theme:e})=>e.colors.secondary.light5};
  }
`,w=(0,o.iK)(i.Z)`
  .ant-modal-body {
    padding: ${({theme:e})=>6*e.gridUnit}px;
  }

  pre {
    font-size: ${({theme:e})=>e.typography.sizes.xs}px;
    font-weight: ${({theme:e})=>e.typography.weights.normal};
    line-height: ${({theme:e})=>e.typography.sizes.l}px;
    height: 375px;
    border: none;
  }
`;function Z({onHide:e,openInSqlLab:t,queries:r,query:s,fetchData:o,show:i,addDangerToast:l,addSuccessToast:c}){const{handleKeyPress:g,handleDataChange:Z,disablePrevious:q,disableNext:x}=(0,y.C)({queries:r,currentQueryId:s.id,fetchData:o}),[C,P]=(0,a.useState)("user"),{id:L,sql:U,executed_sql:S}=s;return(0,h.tZ)("div",{role:"none",onKeyUp:g},(0,h.tZ)(w,{onHide:e,show:i,title:(0,n.t)("Query preview"),footer:[(0,h.tZ)(d.Z,{"data-test":"previous-query",key:"previous-query",disabled:q,onClick:()=>Z(!0)},(0,n.t)("Previous")),(0,h.tZ)(d.Z,{"data-test":"next-query",key:"next-query",disabled:x,onClick:()=>Z(!1)},(0,n.t)("Next")),(0,h.tZ)(d.Z,{"data-test":"open-in-sql-lab",key:"open-in-sql-lab",buttonStyle:"primary",onClick:()=>t(L)},(0,n.t)("Open in SQL Lab"))]},(0,h.tZ)(m,null,(0,n.t)("Tab name")),(0,h.tZ)(v,null,s.tab_name),(0,h.tZ)(b,null,(0,h.tZ)(f,{role:"button","data-test":"toggle-user-sql",className:u()({active:"user"===C}),onClick:()=>P("user")},(0,n.t)("User query")),(0,h.tZ)(f,{role:"button","data-test":"toggle-executed-sql",className:u()({active:"executed"===C}),onClick:()=>P("executed")},(0,n.t)("Executed query"))),(0,h.tZ)(p.Z,{addDangerToast:l,addSuccessToast:c,language:"sql"},("user"===C?U:S)||"")))}g(Z,"useQueryPreviewState{{ handleKeyPress, handleDataChange, disablePrevious, disableNext }}\nuseState{[currentTab, setCurrentTab]('user')}",(()=>[y.C]));const q=(0,c.Z)(Z),x=q;var C,P;(C="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(C.register(m,"QueryTitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(v,"QueryLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(b,"QueryViewToggle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(f,"TabButton","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(w,"StyledModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(Z,"QueryPreviewModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx"),C.register(q,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/query/QueryPreviewModal.tsx")),(P="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&P(e)}}]);