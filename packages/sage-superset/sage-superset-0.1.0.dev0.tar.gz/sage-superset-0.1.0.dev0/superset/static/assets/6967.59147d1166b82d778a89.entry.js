"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[6967],{188104:(e,t,r)=>{r.d(t,{Z:()=>p});var n,a=r(205872),s=r.n(a),o=(r(667294),r(582191)),i=r(751995),l=r(87693),u=r(211965);e=r.hmd(e),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&n(e),"undefined"!=typeof reactHotLoaderGlobal&&reactHotLoaderGlobal.default.signature;const{SubMenu:d}=o.$t,c=i.iK.div`
  display: flex;
  align-items: center;

  & i {
    margin-right: ${({theme:e})=>2*e.gridUnit}px;
  }

  & a {
    display: block;
    width: 150px;
    word-wrap: break-word;
    text-decoration: none;
  }
`,m=i.iK.i`
  margin-top: 2px;
`;function p(e){const{locale:t,languages:r,...n}=e;return(0,u.tZ)(d,s()({"aria-label":"Languages",title:(0,u.tZ)("div",{className:"f16"},(0,u.tZ)(m,{className:`flag ${r[t].flag}`})),icon:(0,u.tZ)(l.Z.TriangleDown,null)},n),Object.keys(r).map((e=>(0,u.tZ)(o.$t.Item,{key:e,style:{whiteSpace:"normal",height:"auto"}},(0,u.tZ)(c,{className:"f16"},(0,u.tZ)("i",{className:`flag ${r[e].flag}`}),(0,u.tZ)("a",{href:r[e].url},r[e].name))))))}var g,h;(g="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(g.register(d,"SubMenu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/LanguagePicker.tsx"),g.register(c,"StyledLabel","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/LanguagePicker.tsx"),g.register(m,"StyledFlag","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/LanguagePicker.tsx"),g.register(p,"LanguagePicker","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/LanguagePicker.tsx")),(h="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&h(e)},456967:(e,t,r)=>{r.d(t,{Z:()=>_});var n,a=r(205872),s=r.n(a),o=r(23279),i=r.n(o),l=r(667294),u=r(751995),d=r(211965),c=r(23525),m=r(582191),p=r(358593),g=r(473727),h=r(87693),f=r(229147),v=r(427600),b=r(199939);e=r.hmd(e),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&n(e);var y="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const Z=u.iK.header`
  background-color: white;
  margin-bottom: 2px;
  &:nth-last-of-type(2) nav {
    margin-bottom: 2px;
  }

  .caret {
    display: none;
  }
  .navbar-brand {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .navbar-brand-text {
    border-left: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    border-right: 1px solid ${({theme:e})=>e.colors.grayscale.light2};
    height: 100%;
    color: ${({theme:e})=>e.colors.grayscale.dark1};
    padding-left: ${({theme:e})=>4*e.gridUnit}px;
    padding-right: ${({theme:e})=>4*e.gridUnit}px;
    margin-right: ${({theme:e})=>6*e.gridUnit}px;
    font-size: ${({theme:e})=>4*e.gridUnit}px;
    float: left;
    display: flex;
    flex-direction: column;
    justify-content: center;

    span {
      max-width: ${({theme:e})=>58*e.gridUnit}px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    @media (max-width: 1127px) {
      display: none;
    }
  }
  .main-nav .ant-menu-submenu-title > svg {
    top: ${({theme:e})=>5.25*e.gridUnit}px;
  }
  @media (max-width: 767px) {
    .navbar-brand {
      float: none;
    }
  }
  .ant-menu-horizontal .ant-menu-item {
    height: 100%;
    line-height: inherit;
  }
  .ant-menu > .ant-menu-item > a {
    padding: ${({theme:e})=>4*e.gridUnit}px;
  }
  @media (max-width: 767px) {
    .ant-menu-item {
      padding: 0 ${({theme:e})=>6*e.gridUnit}px 0
        ${({theme:e})=>3*e.gridUnit}px !important;
    }
    .ant-menu > .ant-menu-item > a {
      padding: 0px;
    }
    .main-nav .ant-menu-submenu-title > svg:nth-child(1) {
      display: none;
    }
    .ant-menu-item-active > a {
      &:hover {
        color: ${({theme:e})=>e.colors.primary.base} !important;
        background-color: transparent !important;
      }
    }
  }

  .ant-menu-item a {
    &:hover {
      color: ${({theme:e})=>e.colors.grayscale.dark1};
      background-color: ${({theme:e})=>e.colors.primary.light5};
      border-bottom: none;
      margin: 0;
      &:after {
        opacity: 1;
        width: 100%;
      }
    }
  }
`,{SubMenu:w}=m.$t,{useBreakpoint:x}=m.rj;function $({data:{menu:e,brand:t,navbar_right:r,settings:n},isFrontendRoute:a=(()=>!1)}){const[s,o]=(0,l.useState)("horizontal"),u=x(),y=(0,f.fG)();return(0,l.useEffect)((()=>{function e(){window.innerWidth<=767?o("inline"):o("horizontal")}e();const t=i()((()=>e()),10);return window.addEventListener("resize",t),()=>window.removeEventListener("resize",t)}),[]),(0,c.e)(v.KD.standalone)||y.hideNav?(0,d.tZ)(l.Fragment,null):(0,d.tZ)(Z,{className:"top",id:"main-menu",role:"navigation"},(0,d.tZ)(d.xB,{styles:d.iv`
          .ant-menu-submenu.ant-menu-submenu-popup.ant-menu.ant-menu-light.ant-menu-submenu-placement-bottomLeft {
            border-radius: 0px;
          }
          .ant-menu-submenu.ant-menu-submenu-popup.ant-menu.ant-menu-light {
            border-radius: 0px;
          }
        `}),(0,d.tZ)(m.X2,null,(0,d.tZ)(m.JX,{md:16,xs:24},(0,d.tZ)(p.u,{id:"brand-tooltip",placement:"bottomLeft",title:t.tooltip,arrowPointAtCenter:!0},(0,d.tZ)("a",{className:"navbar-brand",href:t.path},(0,d.tZ)("img",{width:t.width,src:t.icon,alt:t.alt}))),t.text&&(0,d.tZ)("div",{className:"navbar-brand-text"},(0,d.tZ)("span",null,t.text)),(0,d.tZ)(m.$t,{mode:s,"data-test":"navbar-top",className:"main-nav"},e.map((e=>{var t;return(({label:e,childs:t,url:r,index:n,isFrontendRoute:a})=>r&&a?(0,d.tZ)(m.$t.Item,{key:e,role:"presentation"},(0,d.tZ)(g.rU,{role:"button",to:r},e)):r?(0,d.tZ)(m.$t.Item,{key:e},(0,d.tZ)("a",{href:r},e)):(0,d.tZ)(w,{key:n,title:e,icon:"inline"===s?(0,d.tZ)(l.Fragment,null):(0,d.tZ)(h.Z.TriangleDown,null)},null==t?void 0:t.map(((e,t)=>"string"==typeof e&&"-"===e?(0,d.tZ)(m.$t.Divider,{key:`$${t}`}):"string"!=typeof e?(0,d.tZ)(m.$t.Item,{key:`${e.label}`},e.isFrontendRoute?(0,d.tZ)(g.rU,{to:e.url||""},e.label):(0,d.tZ)("a",{href:e.url},e.label)):null))))({...e,isFrontendRoute:a(e.url),childs:null==(t=e.childs)?void 0:t.map((e=>"string"==typeof e?e:{...e,isFrontendRoute:a(e.url)}))})})))),(0,d.tZ)(m.JX,{md:8,xs:24},(0,d.tZ)(b.Z,{align:u.md?"flex-end":"flex-start",settings:n,navbarRight:r,isFrontendRoute:a}))))}function _({data:e,...t}){const r={...e},n={Security:!0,Manage:!0},a=[],o=[];return r.menu.forEach((e=>{if(!e)return;const t=[],r={...e};e.childs&&(e.childs.forEach((e=>{("string"==typeof e||e.label)&&t.push(e)})),r.childs=t),n.hasOwnProperty(e.name)?o.push(r):a.push(r)})),r.menu=a,r.settings=o,(0,d.tZ)($,s()({data:r},t))}var P,k;y($,"useState{[showMenu, setMenu]('horizontal')}\nuseBreakpoint{screens}\nuseUiConfig{uiConig}\nuseEffect{}",(()=>[x,f.fG])),(P="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&(P.register(Z,"StyledHeader","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/Menu.tsx"),P.register(w,"SubMenu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/Menu.tsx"),P.register(x,"useBreakpoint","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/Menu.tsx"),P.register($,"Menu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/Menu.tsx"),P.register(_,"MenuWrapper","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/Menu.tsx")),(k="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&k(e)},199939:(e,t,r)=>{r.d(t,{Z:()=>x}),r(667294);var n,a=r(582191),s=r(455867),o=r(211965),i=r(751995),l=r(473727),u=r(87693),d=r(870695),c=r(137703),m=r(188104);e=r.hmd(e),(n="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.enterModule:void 0)&&n(e);var p="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default.signature:function(e){return e};const g=[{label:(0,s.t)("SQL query"),url:"/superset/sqllab?new=true",icon:"fa-fw fa-search",perm:"can_sqllab",view:"Superset"},{label:(0,s.t)("Chart"),url:"/chart/add",icon:"fa-fw fa-bar-chart",perm:"can_write",view:"Chart"},{label:(0,s.t)("Dashboard"),url:"/dashboard/new",icon:"fa-fw fa-dashboard",perm:"can_write",view:"Dashboard"}],h=e=>o.iv`
  padding: ${1.5*e.gridUnit}px ${4*e.gridUnit}px
    ${4*e.gridUnit}px ${7*e.gridUnit}px;
  color: ${e.colors.grayscale.base};
  font-size: ${e.typography.sizes.xs}px;
  white-space: nowrap;
`,f=i.iK.div`
  color: ${({theme:e})=>e.colors.primary.dark1};
`,v=i.iK.div`
  display: flex;
  flex-direction: row;
  justify-content: ${({align:e})=>e};
  align-items: center;
  margin-right: ${({theme:e})=>e.gridUnit}px;
  .ant-menu-submenu-title > svg {
    top: ${({theme:e})=>5.25*e.gridUnit}px;
  }
`,b=i.iK.a`
  padding-right: ${({theme:e})=>e.gridUnit}px;
  padding-left: ${({theme:e})=>e.gridUnit}px;
`,{SubMenu:y}=a.$t,Z=({align:e,settings:t,navbarRight:r,isFrontendRoute:n})=>{const{roles:i}=(0,c.v9)((e=>e.user)),p=(0,d.Z)("can_sqllab","Superset",i),Z=(0,d.Z)("can_write","Dashboard",i),w=(0,d.Z)("can_write","Chart",i),x=p||w||Z;return(0,o.tZ)(v,{align:e},(0,o.tZ)(a.$t,{mode:"horizontal"},!r.user_is_anonymous&&x&&(0,o.tZ)(y,{"data-test":"new-dropdown",title:(0,o.tZ)(f,{"data-test":"new-dropdown-icon",className:"fa fa-plus"}),icon:(0,o.tZ)(u.Z.TriangleDown,null)},g.map((e=>(0,d.Z)(e.perm,e.view,i)&&(0,o.tZ)(a.$t.Item,{key:e.label},(0,o.tZ)("a",{href:e.url},(0,o.tZ)("i",{"data-test":`menu-item-${e.label}`,className:`fa ${e.icon}`})," ",e.label))))),(0,o.tZ)(y,{title:(0,s.t)("Settings"),icon:(0,o.tZ)(u.Z.TriangleDown,{iconSize:"xl"})},t.map(((e,r)=>{var s;return[(0,o.tZ)(a.$t.ItemGroup,{key:`${e.label}`,title:e.label},null==(s=e.childs)?void 0:s.map((e=>"string"!=typeof e?(0,o.tZ)(a.$t.Item,{key:`${e.label}`},n(e.url)?(0,o.tZ)(l.rU,{to:e.url||""},e.label):(0,o.tZ)("a",{href:e.url},e.label)):null))),r<t.length-1&&(0,o.tZ)(a.$t.Divider,null)]})),!r.user_is_anonymous&&[(0,o.tZ)(a.$t.Divider,{key:"user-divider"}),(0,o.tZ)(a.$t.ItemGroup,{key:"user-section",title:(0,s.t)("User")},r.user_profile_url&&(0,o.tZ)(a.$t.Item,{key:"profile"},(0,o.tZ)("a",{href:r.user_profile_url},(0,s.t)("Profile"))),r.user_info_url&&(0,o.tZ)(a.$t.Item,{key:"info"},(0,o.tZ)("a",{href:r.user_info_url},(0,s.t)("Info"))),(0,o.tZ)(a.$t.Item,{key:"logout"},(0,o.tZ)("a",{href:r.user_logout_url},(0,s.t)("Logout"))))],(r.version_string||r.version_sha)&&[(0,o.tZ)(a.$t.Divider,{key:"version-info-divider"}),(0,o.tZ)(a.$t.ItemGroup,{key:"about-section",title:(0,s.t)("About")},(0,o.tZ)("div",{className:"about-section"},r.show_watermark&&(0,o.tZ)("div",{css:h},(0,s.t)("Powered by Apache Superset")),r.version_string&&(0,o.tZ)("div",{css:h},"Version: ",r.version_string),r.version_sha&&(0,o.tZ)("div",{css:h},"SHA: ",r.version_sha),r.build_number&&(0,o.tZ)("div",{css:h},"Build: ",r.build_number)))]),r.show_language_picker&&(0,o.tZ)(m.Z,{locale:r.locale,languages:r.languages})),r.documentation_url&&(0,o.tZ)(b,{href:r.documentation_url,target:"_blank",rel:"noreferrer",title:(0,s.t)("Documentation")},(0,o.tZ)("i",{className:"fa fa-question"})," "),r.bug_report_url&&(0,o.tZ)(b,{href:r.bug_report_url,target:"_blank",rel:"noreferrer",title:(0,s.t)("Report a bug")},(0,o.tZ)("i",{className:"fa fa-bug"})),r.user_is_anonymous&&(0,o.tZ)(b,{href:r.user_login_url},(0,o.tZ)("i",{className:"fa fa-fw fa-sign-in"}),(0,s.t)("Login")))};p(Z,"useSelector{{ roles }}",(()=>[c.v9]));const w=Z,x=w;var $,_;($="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.default:void 0)&&($.register(g,"dropdownItems","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(h,"versionInfoStyles","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(f,"StyledI","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(v,"StyledDiv","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(b,"StyledAnchor","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(y,"SubMenu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(Z,"RightMenu","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx"),$.register(w,"default","/Users/chenming/PycharmProjects/venv/superset/superset-frontend/src/views/components/MenuRight.tsx")),(_="undefined"!=typeof reactHotLoaderGlobal?reactHotLoaderGlobal.leaveModule:void 0)&&_(e)}}]);