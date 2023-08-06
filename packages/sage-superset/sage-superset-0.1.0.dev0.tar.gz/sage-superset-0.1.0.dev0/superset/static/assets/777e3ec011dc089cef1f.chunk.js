(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[665],{545578:(e,t,a)=>{var r=a(267206),s=a(345652);e.exports=function(e,t){return e&&e.length?s(e,r(t,2)):[]}},727989:(e,t,a)=>{"use strict";a.d(t,{Z:()=>v});var r,s=a(667294),o=a(751995),n=a(455867),l=a(835932),i=a(574520),d=a(582191),c=a(34858),u=a(211965);e=a.hmd(e),(r="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&r(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const m=o.iK.div`
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
`,g=({resourceName:e,resourceLabel:t,passwordsNeededMessage:a,confirmOverwriteMessage:r,addDangerToast:o,onModelImport:p,show:g,onHide:f,passwordFields:v=[],setPasswordFields:b=(()=>{})})=>{const[y,w]=(0,s.useState)(!0),[C,Z]=(0,s.useState)({}),[x,S]=(0,s.useState)(!1),[_,E]=(0,s.useState)(!1),[P,L]=(0,s.useState)([]),[M,H]=(0,s.useState)(!1),I=()=>{L([]),b([]),Z({}),S(!1),E(!1),H(!1)},{state:{alreadyExists:U,passwordsNeeded:T},importResource:D}=(0,c.PW)(e,t,(e=>{I(),o(e)}));(0,s.useEffect)((()=>{b(T),T.length>0&&H(!1)}),[T,b]),(0,s.useEffect)((()=>{S(U.length>0),U.length>0&&H(!1)}),[U,S]);return y&&g&&w(!1),(0,u.tZ)(i.Z,{name:"model",className:"import-model-modal",disablePrimaryButton:0===P.length||x&&!_||M,onHandledPrimaryAction:()=>{var e;(null==(e=P[0])?void 0:e.originFileObj)instanceof File&&(H(!0),D(P[0].originFileObj,C,_).then((e=>{e&&(I(),p())})))},onHide:()=>{w(!0),f(),I()},primaryButtonName:x?(0,n.t)("Overwrite"):(0,n.t)("Import"),primaryButtonType:x?"danger":"primary",width:"750px",show:g,title:(0,u.tZ)("h4",null,(0,n.t)("Import %s",t))},(0,u.tZ)(h,null,(0,u.tZ)(d.gq,{name:"modelFile",id:"modelFile","data-test":"model-file-input",accept:".yaml,.json,.yml,.zip",fileList:P,onChange:e=>{L([{...e.file,status:"done"}])},onRemove:e=>(L(P.filter((t=>t.uid!==e.uid))),!1),customRequest:()=>{}},(0,u.tZ)(l.Z,{loading:M},"Select file"))),0===v.length?null:(0,u.tZ)(s.Fragment,null,(0,u.tZ)("h5",null,"Database passwords"),(0,u.tZ)(m,null,a),v.map((e=>(0,u.tZ)(h,{key:`password-for-${e}`},(0,u.tZ)("div",{className:"control-label"},e,(0,u.tZ)("span",{className:"required"},"*")),(0,u.tZ)("input",{name:`password-${e}`,autoComplete:`password-${e}`,type:"password",value:C[e],onChange:t=>Z({...C,[e]:t.target.value})}))))),x?(0,u.tZ)(s.Fragment,null,(0,u.tZ)(h,null,(0,u.tZ)("div",{className:"confirm-overwrite"},r),(0,u.tZ)("div",{className:"control-label"},(0,n.t)('Type "%s" to confirm',(0,n.t)("OVERWRITE"))),(0,u.tZ)("input",{"data-test":"overwrite-modal-input",id:"overwrite",type:"text",onChange:e=>{var t,a;const r=null!=(t=null==(a=e.currentTarget)?void 0:a.value)?t:"";E(r.toUpperCase()===(0,n.t)("OVERWRITE"))}}))):null)};p(g,"useState{[isHidden, setIsHidden](true)}\nuseState{[passwords, setPasswords]({})}\nuseState{[needsOverwriteConfirm, setNeedsOverwriteConfirm](false)}\nuseState{[confirmedOverwrite, setConfirmedOverwrite](false)}\nuseState{[fileList, setFileList]([])}\nuseState{[importingModel, setImportingModel](false)}\nuseImportResource{{ state: { alreadyExists, passwordsNeeded }, importResource, }}\nuseEffect{}\nuseEffect{}",(()=>[c.PW]));const f=g,v=f;var b,y;(b="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(b.register(m,"HelperMessage","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),b.register(h,"StyledInputContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),b.register(g,"ImportModelsModal","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx"),b.register(f,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/components/ImportModal/index.tsx")),(y="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&y(e)},413434:(e,t,a)=>{"use strict";a.r(t),a.d(t,{default:()=>B});var r,s=a(545578),o=a.n(s),n=a(751995),l=a(455867),i=a(311064),d=a(431069),c=a(667294),u=a(115926),p=a.n(u),m=a(730381),h=a.n(m),g=a(591877),f=a(440768),v=a(34858),b=a(232228),y=a(419259),w=a(620755),C=a(236674),Z=a(550859),x=a(838703),S=a(961337),_=a(414114),E=a(983673),P=a(727989),L=a(358593),M=a(87693),H=a(301510),I=a(700362),U=a(608272),T=a(679789),D=a(834024),R=a(211965);e=a.hmd(e),(r="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&r(e);var F="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const N=n.iK.div`
  align-items: center;
  display: flex;

  a {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
  }

  svg {
    margin-right: ${({theme:e})=>e.gridUnit}px;
  }
`,k=(0,l.t)('The passwords for the databases below are needed in order to import them together with the charts. Please note that the "Secure Extra" and "Certificate" sections of the database configuration are not present in export files, and should be added manually after the import if they are needed.'),$=(0,l.t)("You are importing one or more charts that already exist. Overwriting might cause you to lose some of your work. Are you sure you want to overwrite?");(0,I.Z)();const A=(0,i.Z)(),O=async(e="",t,a)=>{var r;const s=e?{filters:[{col:"table_name",opr:"sw",value:e}]}:{},n=p().encode({columns:["datasource_name","datasource_id"],keys:["none"],order_column:"table_name",order_direction:"asc",page:t,page_size:a,...s}),{json:l={}}=await d.Z.get({endpoint:`/api/v1/dataset/?q=${n}`}),i=null==l||null==(r=l.result)?void 0:r.map((({table_name:e,id:t})=>({label:e,value:t})));return{data:o()(i,"value"),totalCount:null==l?void 0:l.count}},z=n.iK.div`
  color: ${({theme:e})=>e.colors.grayscale.base};
`;function G(e){const{addDangerToast:t,addSuccessToast:a}=e,{state:{loading:r,resourceCount:s,resourceCollection:o,bulkSelectEnabled:n},setResourceCollection:i,hasPerm:u,fetchData:m,toggleBulkSelect:_,refreshData:I}=(0,v.Yi)("chart",(0,l.t)("chart"),t),F=(0,c.useMemo)((()=>o.map((e=>e.id))),[o]),[G,j]=(0,v.NE)("chart",F,t),{sliceCurrentlyEditing:B,handleChartUpdated:V,openChartEditModal:q,closeChartEditModal:W}=(0,v.fF)(i,o),[Y,K]=(0,c.useState)(!1),[X,J]=(0,c.useState)([]),[Q,ee]=(0,c.useState)(!1),{userId:te}=e.user,ae=(0,S.OH)(null==te?void 0:te.toString(),null),re=u("can_write"),se=u("can_write"),oe=u("can_write"),ne=u("can_export")&&(0,g.cr)(g.TT.VERSIONED_EXPORT),le=[{id:"changed_on_delta_humanized",desc:!0}],ie=e=>{const t=e.map((({id:e})=>e));(0,b.Z)("chart",t,(()=>{ee(!1)})),ee(!0)},de=(0,c.useMemo)((()=>[...e.user.userId?[{Cell:({row:{original:{id:e}}})=>(0,R.tZ)(C.Z,{itemId:e,saveFaveStar:G,isStarred:j[e]}),Header:"",id:"id",disableSortBy:!0,size:"sm"}]:[],{Cell:({row:{original:{url:e,slice_name:t,certified_by:a,certification_details:r,description:s}}})=>(0,R.tZ)(N,null,(0,R.tZ)("a",{href:e,"data-test":`${t}-list-chart-title`},a&&(0,R.tZ)(c.Fragment,null,(0,R.tZ)(T.Z,{certifiedBy:a,details:r})," "),t),s&&(0,R.tZ)(U.Z,{tooltip:s,viewBox:"0 -1 24 24"})),Header:(0,l.t)("Chart"),accessor:"slice_name"},{Cell:({row:{original:{viz_type:e}}})=>{var t;return(null==(t=A.get(e))?void 0:t.name)||e},Header:(0,l.t)("Visualization type"),accessor:"viz_type",size:"xxl"},{Cell:({row:{original:{datasource_name_text:e,datasource_url:t}}})=>(0,R.tZ)("a",{href:t},e),Header:(0,l.t)("Dataset"),accessor:"datasource_id",disableSortBy:!0,size:"xl"},{Cell:({row:{original:{last_saved_by:e,changed_by_url:t}}})=>(0,R.tZ)("a",{href:t},null!=e&&e.first_name?`${null==e?void 0:e.first_name} ${null==e?void 0:e.last_name}`:null),Header:(0,l.t)("Modified by"),accessor:"last_saved_by.first_name",size:"xl"},{Cell:({row:{original:{last_saved_at:e}}})=>(0,R.tZ)("span",{className:"no-wrap"},e?h().utc(e).fromNow():null),Header:(0,l.t)("Last modified"),accessor:"last_saved_at",size:"xl"},{accessor:"owners",hidden:!0,disableSortBy:!0},{Cell:({row:{original:{created_by:e}}})=>e?`${e.first_name} ${e.last_name}`:"",Header:(0,l.t)("Created by"),accessor:"created_by",disableSortBy:!0,size:"xl"},{Cell:({row:{original:e}})=>se||oe||ne?(0,R.tZ)(z,{className:"actions"},oe&&(0,R.tZ)(y.Z,{title:(0,l.t)("Please confirm"),description:(0,R.tZ)(c.Fragment,null,(0,l.t)("Are you sure you want to delete")," ",(0,R.tZ)("b",null,e.slice_name),"?"),onConfirm:()=>(0,f.Gm)(e,a,t,I)},(e=>(0,R.tZ)(L.u,{id:"delete-action-tooltip",title:(0,l.t)("Delete"),placement:"bottom"},(0,R.tZ)("span",{"data-test":"trash",role:"button",tabIndex:0,className:"action-button",onClick:e},(0,R.tZ)(M.Z.Trash,null))))),ne&&(0,R.tZ)(L.u,{id:"export-action-tooltip",title:(0,l.t)("Export"),placement:"bottom"},(0,R.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>ie([e])},(0,R.tZ)(M.Z.Share,null))),se&&(0,R.tZ)(L.u,{id:"edit-action-tooltip",title:(0,l.t)("Edit"),placement:"bottom"},(0,R.tZ)("span",{role:"button",tabIndex:0,className:"action-button",onClick:()=>q(e)},(0,R.tZ)(M.Z.EditAlt,{"data-test":"edit-alt"})))):null,Header:(0,l.t)("Actions"),id:"actions",disableSortBy:!0,hidden:!se&&!oe}]),[se,oe,ne,...e.user.userId?[j]:[]]),ce=(0,c.useMemo)((()=>({Header:(0,l.t)("Favorite"),id:"id",urlDisplay:"favorite",input:"select",operator:Z.p.chartIsFav,unfilteredLabel:(0,l.t)("Any"),selects:[{label:(0,l.t)("Yes"),value:!0},{label:(0,l.t)("No"),value:!1}]})),[]),ue=(0,c.useMemo)((()=>[{Header:(0,l.t)("Owner"),id:"owners",input:"select",operator:Z.p.relationManyMany,unfilteredLabel:(0,l.t)("All"),fetchSelects:(0,f.tm)("chart","owners",(0,f.v$)((e=>t((0,l.t)("An error occurred while fetching chart owners values: %s",e)))),e.user),paginate:!0},{Header:(0,l.t)("Created by"),id:"created_by",input:"select",operator:Z.p.relationOneMany,unfilteredLabel:(0,l.t)("All"),fetchSelects:(0,f.tm)("chart","created_by",(0,f.v$)((e=>t((0,l.t)("An error occurred while fetching chart created by values: %s",e)))),e.user),paginate:!0},{Header:(0,l.t)("Viz type"),id:"viz_type",input:"select",operator:Z.p.equals,unfilteredLabel:(0,l.t)("All"),selects:A.keys().filter((e=>{var t;return(0,H.X3)((null==(t=A.get(e))?void 0:t.behaviors)||[])})).map((e=>{var t;return{label:(null==(t=A.get(e))?void 0:t.name)||e,value:e}})).sort(((e,t)=>e.label&&t.label?e.label>t.label?1:e.label<t.label?-1:0:0))},{Header:(0,l.t)("Dataset"),id:"datasource_id",input:"select",operator:Z.p.equals,unfilteredLabel:(0,l.t)("All"),fetchSelects:O,paginate:!0},...e.user.userId?[ce]:[],{Header:(0,l.t)("Certified"),id:"id",urlDisplay:"certified",input:"select",operator:Z.p.chartIsCertified,unfilteredLabel:(0,l.t)("Any"),selects:[{label:(0,l.t)("Yes"),value:!0},{label:(0,l.t)("No"),value:!1}]},{Header:(0,l.t)("Search"),id:"slice_name",input:"search",operator:Z.p.chartAllText}]),[t,ce,e.user]),pe=[{desc:!1,id:"slice_name",label:(0,l.t)("Alphabetical"),value:"alphabetical"},{desc:!0,id:"changed_on_delta_humanized",label:(0,l.t)("Recently modified"),value:"recently_modified"},{desc:!1,id:"changed_on_delta_humanized",label:(0,l.t)("Least recently modified"),value:"least_recently_modified"}];function me(e){return(0,R.tZ)(D.Z,{chart:e,showThumbnails:ae?ae.thumbnails:(0,g.cr)(g.TT.THUMBNAILS),hasPerm:u,openChartEditModal:q,bulkSelectEnabled:n,addDangerToast:t,addSuccessToast:a,refreshData:I,loading:r,favoriteStatus:j[e.id],saveFavoriteStatus:G,handleBulkChartExport:ie})}const he=[];return(oe||ne)&&he.push({name:(0,l.t)("Bulk select"),buttonStyle:"secondary","data-test":"bulk-select",onClick:_}),re&&(he.push({name:(0,R.tZ)(c.Fragment,null,(0,R.tZ)("i",{className:"fa fa-plus"})," ",(0,l.t)("Chart")),buttonStyle:"primary",onClick:()=>{window.location.assign("/chart/add")}}),(0,g.cr)(g.TT.VERSIONED_EXPORT)&&he.push({name:(0,R.tZ)(L.u,{id:"import-tooltip",title:(0,l.t)("Import charts"),placement:"bottomRight"},(0,R.tZ)(M.Z.Import,{"data-test":"import-button"})),buttonStyle:"link",onClick:()=>{K(!0)}})),(0,R.tZ)(c.Fragment,null,(0,R.tZ)(w.Z,{name:(0,l.t)("Charts"),buttons:he}),B&&(0,R.tZ)(E.Z,{onHide:W,onSave:V,show:!0,slice:B}),(0,R.tZ)(y.Z,{title:(0,l.t)("Please confirm"),description:(0,l.t)("Are you sure you want to delete the selected charts?"),onConfirm:function(e){d.Z.delete({endpoint:`/api/v1/chart/?q=${p().encode(e.map((({id:e})=>e)))}`}).then((({json:e={}})=>{I(),a(e.message)}),(0,f.v$)((e=>t((0,l.t)("There was an issue deleting the selected charts: %s",e)))))}},(e=>{const t=[];return oe&&t.push({key:"delete",name:(0,l.t)("Delete"),type:"danger",onSelect:e}),ne&&t.push({key:"export",name:(0,l.t)("Export"),type:"primary",onSelect:ie}),(0,R.tZ)(Z.Z,{bulkActions:t,bulkSelectEnabled:n,cardSortSelectOptions:pe,className:"chart-list-view",columns:de,count:s,data:o,disableBulkSelect:_,fetchData:m,filters:ue,initialSort:le,loading:r,pageSize:25,renderCard:me,showThumbnails:ae?ae.thumbnails:(0,g.cr)(g.TT.THUMBNAILS),defaultViewMode:(0,g.cr)(g.TT.LISTVIEWS_DEFAULT_CARD_VIEW)?"card":"table"})})),(0,R.tZ)(P.Z,{resourceName:"chart",resourceLabel:(0,l.t)("chart"),passwordsNeededMessage:k,confirmOverwriteMessage:$,addDangerToast:t,addSuccessToast:a,onModelImport:()=>{K(!1),I(),a((0,l.t)("Chart imported"))},show:Y,onHide:()=>{K(!1)},passwordFields:X,setPasswordFields:J}),Q&&(0,R.tZ)(x.Z,null))}F(G,"useListViewResource{{ state: { loading, resourceCount: chartCount, resourceCollection: charts, bulkSelectEnabled, }, setResourceCollection: setCharts, hasPerm, fetchData, toggleBulkSelect, refreshData, }}\nuseMemo{chartIds}\nuseFavoriteStatus{[saveFavoriteStatus, favoriteStatus]}\nuseChartEditModal{{ sliceCurrentlyEditing, handleChartUpdated, openChartEditModal, closeChartEditModal, }}\nuseState{[importingChart, showImportModal](false)}\nuseState{[passwordFields, setPasswordFields]([])}\nuseState{[preparingExport, setPreparingExport](false)}\nuseMemo{columns}\nuseMemo{favoritesFilter}\nuseMemo{filters}",(()=>[v.Yi,v.NE,v.fF]));const j=(0,_.Z)(G),B=j;var V,q;(V="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(V.register(N,"FlexRowContainer","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(25,"PAGE_SIZE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(k,"PASSWORDS_NEEDED_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register($,"CONFIRM_OVERWRITE_MESSAGE","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(A,"registry","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(O,"createFetchDatasets","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(z,"Actions","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(G,"ChartList","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx"),V.register(j,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/CRUD/chart/ChartList.tsx")),(q="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&q(e)}}]);