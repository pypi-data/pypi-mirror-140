"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[9173],{727989:(e,t,r)=>{r.d(t,{Z:()=>g});var a,s=r(667294),o=r(751995),n=r(455867),i=r(835932),l=r(574520),d=r(582191),u=r(34858),c=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const m=o.iK.div`
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
`,v=({resourceName:e,resourceLabel:t,passwordsNeededMessage:r,confirmOverwriteMessage:a,addDangerToast:o,onModelImport:p,show:v,onHide:y,passwordFields:g=[],setPasswordFields:f=(()=>{})})=>{const[b,w]=(0,s.useState)(!0),[S,x]=(0,s.useState)({}),[Z,P]=(0,s.useState)(!1),[C,q]=(0,s.useState)(!1),[L,H]=(0,s.useState)([]),[k,D]=(0,s.useState)(!1),U=()=>{H([]),f([]),x({}),P(!1),q(!1),D(!1)},{state:{alreadyExists:M,passwordsNeeded:$},importResource:E}=(0,u.PW)(e,t,(e=>{U(),o(e)}));(0,s.useEffect)((()=>{f($),$.length>0&&D(!1)}),[$,f]),(0,s.useEffect)((()=>{P(M.length>0),M.length>0&&D(!1)}),[M,P]);return b&&v&&w(!1),(0,c.tZ)(l.Z,{name:"model",className:"import-model-modal",disablePrimaryButton:0===L.length||Z&&!C||k,onHandledPrimaryAction:()=>{var e;(null==(e=L[0])?void 0:e.originFileObj)instanceof File&&(D(!0),E(L[0].originFileObj,S,C).then((e=>{e&&(U(),p())})))},onHide:()=>{w(!0),y(),U()},primaryButtonName:Z?(0,n.t)("Overwrite"):(0,n.t)("Import"),primaryButtonType:Z?"danger":"primary",width:"750px",show:v,title:(0,c.tZ)("h4",null,(0,n.t)("Import %s",t))},(0,c.tZ)(h,null,(0,c.tZ)(d.gq,{name:"modelFile",id:"modelFile","data-test":"model-file-input",accept:".yaml,.json,.yml,.zip",fileList:L,onChange:e=>{H([{...e.file,status:"done"}])},onRemove:e=>(H(L.filter((t=>t.uid!==e.uid))),!1),customRequest:()=>{}},(0,c.tZ)(i.Z,{loading:k},"Select file"))),0===g.length?null:(0,c.tZ)(s.Fragment,null,(0,c.tZ)("h5",null,"Database passwords"),(0,c.tZ)(m,null,r),g.map((e=>(0,c.tZ)(h,{key:`password-for-${e}`},(0,c.tZ)("div",{className:"control-label"},e,(0,c.tZ)("span",{className:"required"},"*")),(0,c.tZ)("input",{name:`password-${e}`,autoComplete:`password-${e}`,type:"password",value:S[e],onChange:t=>x({...S,[e]:t.target.value})}))))),Z?(0,c.tZ)(s.Fragment,null,(0,c.tZ)(h,null,(0,c.tZ)("div",{className:"confirm-overwrite"},a),(0,c.tZ)("div",{className:"control-label"},(0,n.t)('Type "%s" to confirm',(0,n.t)("OVERWRITE"))),(0,c.tZ)("input",{"data-test":"overwrite-modal-input",id:"overwrite",type:"text",onChange:e=>{var t,r;const a=null!=(t=null==(r=e.currentTarget)?void 0:r.value)?t:"";q(a.toUpperCase()===(0,n.t)("OVERWRITE"))}}))):null)};p(v,"useState{[isHidden, setIsHidden](true)}\nuseState{[passwords, setPasswords]({})}\nuseState{[needsOverwriteConfirm, setNeedsOverwriteConfirm](false)}\nuseState{[confirmedOverwrite, setConfirmedOverwrite](false)}\nuseState{[fileList, setFileList]([])}\nuseState{[importingModel, setImportingModel](false)}\nuseImportResource{{ state: { alreadyExists, passwordsNeeded }, importResource, }}\nuseEffect{}\nuseEffect{}",(()=>[u.PW]));const y=v,g=y;var f,b;(f="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(f.register(m,"HelperMessage","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(h,"StyledInputContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(v,"ImportModelsModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),f.register(y,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx")),(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&b(e)},129848:(e,t,r)=>{r.d(t,{Z:()=>u}),r(667294);var a,s=r(751995),o=r(358593),n=r(87693),i=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const l=s.iK.span`
  white-space: nowrap;
  min-width: 100px;
  svg,
  i {
    margin-right: 8px;

    &:hover {
      path {
        fill: ${({theme:e})=>e.colors.primary.base};
      }
    }
  }
`,d=s.iK.span`
  color: ${({theme:e})=>e.colors.grayscale.base};
`;function u({actions:e}){return(0,i.tZ)(l,{className:"actions"},e.map(((e,t)=>{const r=n.Z[e.icon];return e.tooltip?(0,i.tZ)(o.u,{id:`${e.label}-tooltip`,title:e.tooltip,placement:e.placement,key:t},(0,i.tZ)(d,{role:"button",tabIndex:0,className:"action-button","data-test":e.label,onClick:e.onClick},(0,i.tZ)(r,null))):(0,i.tZ)(d,{role:"button",tabIndex:0,className:"action-button",onClick:e.onClick,"data-test":e.label,key:t},(0,i.tZ)(r,null))})))}var c,p;(c="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(c.register(l,"StyledActions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ActionsBar.tsx"),c.register(d,"ActionWrapper","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ActionsBar.tsx"),c.register(u,"ActionsBar","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ListView/ActionsBar.tsx")),(p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&p(e)},952607:(e,t,r)=>{r.r(t),r.d(t,{default:()=>_});var a,s=r(455867),o=r(751995),n=r(431069),i=r(667294),l=r(115926),d=r.n(l),u=r(730381),c=r.n(u),p=r(440768),m=r(976697),h=r(414114),v=r(34858),y=r(419259),g=r(232228),f=r(620755),b=r(550859),w=r(838703),S=r(217198),x=r(129848),Z=r(358593),P=r(495413),C=r(710222),q=r(591877),L=r(727989),H=r(87693),k=r(684858),D=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var U="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const M=(0,s.t)('The passwords for the databases below are needed in order to import them together with the saved queries. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in export files, and should be added manually after the import if they are needed.'),$=(0,s.t)("You are importing one or more saved queries that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?"),E=o.iK.div`
  .count {
    margin-left: 5px;
    color: ${({theme:e})=>e.colors.primary.base};
    text-decoration: underline;
    cursor: pointer;
  }
`,G=o.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
`;function Q({addDangerToast:e,addSuccessToast:t,user:r}){const{state:{loading:a,resourceCount:o,resourceCollection:l,bulkSelectEnabled:u},hasPerm:h,fetchData:U,toggleBulkSelect:Q,refreshData:T}=(0,v.Yi)("saved_query",(0,s.t)("Saved queries"),e),[_,R]=(0,i.useState)(null),[I,N]=(0,i.useState)(null),[j,O]=(0,i.useState)(!1),[z,A]=(0,i.useState)([]),[F,B]=(0,i.useState)(!1),K=h("can_write"),V=h("can_write"),W=h("can_write"),Y=h("can_export")&&(0,q.cr)(q.TT.VERSIONED_EXPORT),X=(0,i.useCallback)((t=>{n.Z.get({endpoint:`/api/v1/saved_query/${t}`}).then((({json:e={}})=>{N({...e.result})}),(0,p.v$)((t=>e((0,s.t)("There was an issue previewing the selected query %s",t)))))}),[e]),J={activeChild:"Saved queries",...P.Y},ee=[];W&&ee.push({name:(0,s.t)("Bulk select"),onClick:Q,buttonStyle:"secondary"}),ee.push({name:(0,D.tZ)(i.Fragment,null,(0,D.tZ)("i",{className:"fa fa-plus"})," ",(0,s.t)("Query")),onClick:()=>{window.open(`${window.location.origin}/superset/sqllab?new=true`)},buttonStyle:"primary"}),K&&(0,q.cr)(q.TT.VERSIONED_EXPORT)&&ee.push({name:(0,D.tZ)(Z.u,{id:"import-tooltip",title:(0,s.t)("Import queries"),placement:"bottomRight","data-test":"import-tooltip-test"},(0,D.tZ)(H.Z.Import,{"data-test":"import-icon"})),buttonStyle:"link",onClick:()=>{O(!0)},"data-test":"import-button"}),J.buttons=ee;const te=e=>{window.open(`${window.location.origin}/superset/sqllab?savedQueryId=${e}`)},re=(0,i.useCallback)((r=>{(0,C.Z)(`${window.location.origin}/superset/sqllab?savedQueryId=${r}`).then((()=>{t((0,s.t)("Link Copied!"))})).catch((()=>{e((0,s.t)("Sorry, your browser does not support copying."))}))}),[e,t]),ae=e=>{const t=e.map((({id:e})=>e));(0,g.Z)("saved_query",t,(()=>{B(!1)})),B(!0)},se=[{id:"changed_on_delta_humanized",desc:!0}],oe=(0,i.useMemo)((()=>[{accessor:"label",Header:(0,s.t)("Name")},{accessor:"database.database_name",Header:(0,s.t)("Database"),size:"xl"},{accessor:"database",hidden:!0,disableSortBy:!0},{accessor:"schema",Header:(0,s.t)("Schema"),size:"xl"},{Cell:({row:{original:{sql_tables:e=[]}}})=>{const t=e.map((e=>e.table)),r=(null==t?void 0:t.shift())||"";return t.length?(0,D.tZ)(E,null,(0,D.tZ)("span",null,r),(0,D.tZ)(m.Z,{placement:"right",title:(0,s.t)("TABLES"),trigger:"click",content:(0,D.tZ)(i.Fragment,null,t.map((e=>(0,D.tZ)(G,{key:e},e))))},(0,D.tZ)("span",{className:"count"},"(+",t.length,")"))):r},accessor:"sql_tables",Header:(0,s.t)("Tables"),size:"xl",disableSortBy:!0},{Cell:({row:{original:{created_on:e}}})=>{const t=new Date(e),r=new Date(Date.UTC(t.getFullYear(),t.getMonth(),t.getDate(),t.getHours(),t.getMinutes(),t.getSeconds(),t.getMilliseconds()));return c()(r).fromNow()},Header:(0,s.t)("Created on"),accessor:"created_on",size:"xl"},{Cell:({row:{original:{changed_on_delta_humanized:e}}})=>e,Header:(0,s.t)("Modified"),accessor:"changed_on_delta_humanized",size:"xl"},{Cell:({row:{original:e}})=>{const t=[{label:"preview-action",tooltip:(0,s.t)("Query preview"),placement:"bottom",icon:"Binoculars",onClick:()=>{X(e.id)}},V&&{label:"edit-action",tooltip:(0,s.t)("Edit query"),placement:"bottom",icon:"Edit",onClick:()=>te(e.id)},{label:"copy-action",tooltip:(0,s.t)("Copy query URL"),placement:"bottom",icon:"Copy",onClick:()=>re(e.id)},Y&&{label:"export-action",tooltip:(0,s.t)("Export query"),placement:"bottom",icon:"Share",onClick:()=>ae([e])},W&&{label:"delete-action",tooltip:(0,s.t)("Delete query"),placement:"bottom",icon:"Trash",onClick:()=>R(e)}].filter((e=>!!e));return(0,D.tZ)(x.Z,{actions:t})},Header:(0,s.t)("Actions"),id:"actions",disableSortBy:!0}]),[W,V,Y,re,X]),ne=(0,i.useMemo)((()=>[{Header:(0,s.t)("Database"),id:"database",input:"select",operator:b.p.relationOneMany,unfilteredLabel:"All",fetchSelects:(0,p.tm)("saved_query","database",(0,p.v$)((t=>e((0,s.t)("An error occurred while fetching dataset datasource values: %s",t))))),paginate:!0},{Header:(0,s.t)("Schema"),id:"schema",input:"select",operator:b.p.equals,unfilteredLabel:"All",fetchSelects:(0,p.wk)("saved_query","schema",(0,p.v$)((t=>e((0,s.t)("An error occurred while fetching schema values: %s",t))))),paginate:!0},{Header:(0,s.t)("Search"),id:"label",input:"search",operator:b.p.allText}]),[e]);return(0,D.tZ)(i.Fragment,null,(0,D.tZ)(f.Z,J),_&&(0,D.tZ)(S.Z,{description:(0,s.t)("This action will permanently delete the saved query."),onConfirm:()=>{_&&(({id:r,label:a})=>{n.Z.delete({endpoint:`/api/v1/saved_query/${r}`}).then((()=>{T(),R(null),t((0,s.t)("Deleted: %s",a))}),(0,p.v$)((t=>e((0,s.t)("There was an issue deleting %s: %s",a,t)))))})(_)},onHide:()=>R(null),open:!0,title:(0,s.t)("Delete Query?")}),I&&(0,D.tZ)(k.Z,{fetchData:X,onHide:()=>N(null),savedQuery:I,queries:l,openInSqlLab:te,show:!0}),(0,D.tZ)(y.Z,{title:(0,s.t)("Please confirm"),description:(0,s.t)("Are you sure you want to delete the selected queries?"),onConfirm:r=>{n.Z.delete({endpoint:`/api/v1/saved_query/?q=${d().encode(r.map((({id:e})=>e)))}`}).then((({json:e={}})=>{T(),t(e.message)}),(0,p.v$)((t=>e((0,s.t)("There was an issue deleting the selected queries: %s",t)))))}},(e=>{const t=[];return W&&t.push({key:"delete",name:(0,s.t)("Delete"),onSelect:e,type:"danger"}),Y&&t.push({key:"export",name:(0,s.t)("Export"),type:"primary",onSelect:ae}),(0,D.tZ)(b.Z,{className:"saved_query-list-view",columns:oe,count:o,data:l,fetchData:U,filters:ne,initialSort:se,loading:a,pageSize:25,bulkActions:t,bulkSelectEnabled:u,disableBulkSelect:Q,highlightRowId:null==I?void 0:I.id})})),(0,D.tZ)(L.Z,{resourceName:"saved_query",resourceLabel:(0,s.t)("queries"),passwordsNeededMessage:M,confirmOverwriteMessage:$,addDangerToast:e,addSuccessToast:t,onModelImport:()=>{O(!1),T(),t((0,s.t)("Query imported"))},show:j,onHide:()=>{O(!1)},passwordFields:z,setPasswordFields:A}),F&&(0,D.tZ)(w.Z,null))}U(Q,"useListViewResource{{ state: { loading, resourceCount: queryCount, resourceCollection: queries, bulkSelectEnabled, }, hasPerm, fetchData, toggleBulkSelect, refreshData, }}\nuseState{[queryCurrentlyDeleting, setQueryCurrentlyDeleting](null)}\nuseState{[savedQueryCurrentlyPreviewing, setSavedQueryCurrentlyPreviewing](null)}\nuseState{[importingSavedQuery, showImportModal](false)}\nuseState{[passwordFields, setPasswordFields]([])}\nuseState{[preparingExport, setPreparingExport](false)}\nuseCallback{handleSavedQueryPreview}\nuseCallback{copyQueryLink}\nuseMemo{columns}\nuseMemo{filters}",(()=>[v.Yi]));const T=(0,h.Z)(Q),_=T;var R,I;(R="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(R.register(25,"PAGE_SIZE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register(M,"PASSWORDS_NEEDED_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register($,"CONFIRM_OVERWRITE_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register(E,"StyledTableLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register(G,"StyledPopoverItem","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register(Q,"SavedQueryList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx"),R.register(T,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryList.tsx")),(I="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&I(e)},684858:(e,t,r)=>{r.d(t,{Z:()=>f}),r(667294);var a,s=r(751995),o=r(455867),n=r(574520),i=r(835932),l=r(331673),d=r(414114),u=r(14025),c=r(211965);e=r.hmd(e),(a="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&a(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const m=s.iK.div`
  color: ${({theme:e})=>e.colors.secondary.light2};
  font-size: ${({theme:e})=>e.typography.sizes.s-1}px;
  margin-bottom: 0;
  text-transform: uppercase;
`,h=s.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.dark2};
  font-size: ${({theme:e})=>e.typography.sizes.m-1}px;
  padding: 4px 0 16px 0;
`,v=(0,s.iK)(n.Z)`
  .ant-modal-content {
  }

  .ant-modal-body {
    padding: 24px;
  }

  pre {
    font-size: ${({theme:e})=>e.typography.sizes.xs}px;
    font-weight: ${({theme:e})=>e.typography.weights.normal};
    line-height: ${({theme:e})=>e.typography.sizes.l}px;
    height: 375px;
    border: none;
  }
`,y=({fetchData:e,onHide:t,openInSqlLab:r,queries:a,savedQuery:s,show:n,addDangerToast:d,addSuccessToast:p})=>{const{handleKeyPress:y,handleDataChange:g,disablePrevious:f,disableNext:b}=(0,u.C)({queries:a,currentQueryId:s.id,fetchData:e});return(0,c.tZ)("div",{role:"none",onKeyUp:y},(0,c.tZ)(v,{onHide:t,show:n,title:(0,o.t)("Query preview"),footer:[(0,c.tZ)(i.Z,{"data-test":"previous-saved-query",key:"previous-saved-query",disabled:f,onClick:()=>g(!0)},(0,o.t)("Previous")),(0,c.tZ)(i.Z,{"data-test":"next-saved-query",key:"next-saved-query",disabled:b,onClick:()=>g(!1)},(0,o.t)("Next")),(0,c.tZ)(i.Z,{"data-test":"open-in-sql-lab",key:"open-in-sql-lab",buttonStyle:"primary",onClick:()=>r(s.id)},(0,o.t)("Open in SQL Lab"))]},(0,c.tZ)(m,null,(0,o.t)("Query name")),(0,c.tZ)(h,null,s.label),(0,c.tZ)(l.Z,{language:"sql",addDangerToast:d,addSuccessToast:p},s.sql||"")))};p(y,"useQueryPreviewState{{ handleKeyPress, handleDataChange, disablePrevious, disableNext }}",(()=>[u.C]));const g=(0,d.Z)(y),f=g;var b,w;(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(b.register(m,"QueryTitle","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryPreviewModal.tsx"),b.register(h,"QueryLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryPreviewModal.tsx"),b.register(v,"StyledModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryPreviewModal.tsx"),b.register(y,"SavedQueryPreviewModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryPreviewModal.tsx"),b.register(g,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/data/savedquery/SavedQueryPreviewModal.tsx")),(w="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&w(e)}}]);