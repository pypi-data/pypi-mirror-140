/*! For license information please see fe8442ce.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[8873],{63207:(t,i,e)=>{e(65660),e(15112);var n=e(9672),s=e(87156),o=e(50856),a=e(48175);(0,n.k)({_template:o.d`
    <style>
      :host {
        @apply --layout-inline;
        @apply --layout-center-center;
        position: relative;

        vertical-align: middle;

        fill: var(--iron-icon-fill-color, currentcolor);
        stroke: var(--iron-icon-stroke-color, none);

        width: var(--iron-icon-width, 24px);
        height: var(--iron-icon-height, 24px);
        @apply --iron-icon;
      }

      :host([hidden]) {
        display: none;
      }
    </style>
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:a.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(t){var i=(t||"").split(":");this._iconName=i.pop(),this._iconsetName=i.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(t){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,s.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,s.vz)(this.root).appendChild(this._img))}})},72986:(t,i,e)=>{e.d(i,{z:()=>a});e(48175);var n=e(87156),s=e(74460),o=new Set;const a={properties:{_parentResizable:{type:Object,observer:"_parentResizableChanged"},_notifyingDescendant:{type:Boolean,value:!1}},listeners:{"iron-request-resize-notifications":"_onIronRequestResizeNotifications"},created:function(){this._interestedResizables=[],this._boundNotifyResize=this.notifyResize.bind(this),this._boundOnDescendantIronResize=this._onDescendantIronResize.bind(this)},attached:function(){this._requestResizeNotifications()},detached:function(){this._parentResizable?this._parentResizable.stopResizeNotificationsFor(this):(o.delete(this),window.removeEventListener("resize",this._boundNotifyResize)),this._parentResizable=null},notifyResize:function(){this.isAttached&&(this._interestedResizables.forEach((function(t){this.resizerShouldNotify(t)&&this._notifyDescendant(t)}),this),this._fireResize())},assignParentResizable:function(t){this._parentResizable&&this._parentResizable.stopResizeNotificationsFor(this),this._parentResizable=t,t&&-1===t._interestedResizables.indexOf(this)&&(t._interestedResizables.push(this),t._subscribeIronResize(this))},stopResizeNotificationsFor:function(t){var i=this._interestedResizables.indexOf(t);i>-1&&(this._interestedResizables.splice(i,1),this._unsubscribeIronResize(t))},_subscribeIronResize:function(t){t.addEventListener("iron-resize",this._boundOnDescendantIronResize)},_unsubscribeIronResize:function(t){t.removeEventListener("iron-resize",this._boundOnDescendantIronResize)},resizerShouldNotify:function(t){return!0},_onDescendantIronResize:function(t){this._notifyingDescendant?t.stopPropagation():s.my||this._fireResize()},_fireResize:function(){this.fire("iron-resize",null,{node:this,bubbles:!1})},_onIronRequestResizeNotifications:function(t){var i=(0,n.vz)(t).rootTarget;i!==this&&(i.assignParentResizable(this),this._notifyDescendant(i),t.stopPropagation())},_parentResizableChanged:function(t){t&&window.removeEventListener("resize",this._boundNotifyResize)},_notifyDescendant:function(t){this.isAttached&&(this._notifyingDescendant=!0,t.notifyResize(),this._notifyingDescendant=!1)},_requestResizeNotifications:function(){if(this.isAttached)if("loading"===document.readyState){var t=this._requestResizeNotifications.bind(this);document.addEventListener("readystatechange",(function i(){document.removeEventListener("readystatechange",i),t()}))}else this._findParent(),this._parentResizable?this._parentResizable._interestedResizables.forEach((function(t){t!==this&&t._findParent()}),this):(o.forEach((function(t){t!==this&&t._findParent()}),this),window.addEventListener("resize",this._boundNotifyResize),this.notifyResize())},_findParent:function(){this.assignParentResizable(null),this.fire("iron-request-resize-notifications",null,{node:this,bubbles:!0,cancelable:!0}),this._parentResizable?o.delete(this):o.add(this)}}},54444:(t,i,e)=>{e(48175);var n=e(9672),s=e(87156),o=e(50856);(0,n.k)({_template:o.d`
    <style>
      :host {
        display: block;
        position: absolute;
        outline: none;
        z-index: 1002;
        -moz-user-select: none;
        -ms-user-select: none;
        -webkit-user-select: none;
        user-select: none;
        cursor: default;
      }

      #tooltip {
        display: block;
        outline: none;
        @apply --paper-font-common-base;
        font-size: 10px;
        line-height: 1;
        background-color: var(--paper-tooltip-background, #616161);
        color: var(--paper-tooltip-text-color, white);
        padding: 8px;
        border-radius: 2px;
        @apply --paper-tooltip;
      }

      @keyframes keyFrameScaleUp {
        0% {
          transform: scale(0.0);
        }
        100% {
          transform: scale(1.0);
        }
      }

      @keyframes keyFrameScaleDown {
        0% {
          transform: scale(1.0);
        }
        100% {
          transform: scale(0.0);
        }
      }

      @keyframes keyFrameFadeInOpacity {
        0% {
          opacity: 0;
        }
        100% {
          opacity: var(--paper-tooltip-opacity, 0.9);
        }
      }

      @keyframes keyFrameFadeOutOpacity {
        0% {
          opacity: var(--paper-tooltip-opacity, 0.9);
        }
        100% {
          opacity: 0;
        }
      }

      @keyframes keyFrameSlideDownIn {
        0% {
          transform: translateY(-2000px);
          opacity: 0;
        }
        10% {
          opacity: 0.2;
        }
        100% {
          transform: translateY(0);
          opacity: var(--paper-tooltip-opacity, 0.9);
        }
      }

      @keyframes keyFrameSlideDownOut {
        0% {
          transform: translateY(0);
          opacity: var(--paper-tooltip-opacity, 0.9);
        }
        10% {
          opacity: 0.2;
        }
        100% {
          transform: translateY(-2000px);
          opacity: 0;
        }
      }

      .fade-in-animation {
        opacity: 0;
        animation-delay: var(--paper-tooltip-delay-in, 500ms);
        animation-name: keyFrameFadeInOpacity;
        animation-iteration-count: 1;
        animation-timing-function: ease-in;
        animation-duration: var(--paper-tooltip-duration-in, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .fade-out-animation {
        opacity: var(--paper-tooltip-opacity, 0.9);
        animation-delay: var(--paper-tooltip-delay-out, 0ms);
        animation-name: keyFrameFadeOutOpacity;
        animation-iteration-count: 1;
        animation-timing-function: ease-in;
        animation-duration: var(--paper-tooltip-duration-out, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .scale-up-animation {
        transform: scale(0);
        opacity: var(--paper-tooltip-opacity, 0.9);
        animation-delay: var(--paper-tooltip-delay-in, 500ms);
        animation-name: keyFrameScaleUp;
        animation-iteration-count: 1;
        animation-timing-function: ease-in;
        animation-duration: var(--paper-tooltip-duration-in, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .scale-down-animation {
        transform: scale(1);
        opacity: var(--paper-tooltip-opacity, 0.9);
        animation-delay: var(--paper-tooltip-delay-out, 500ms);
        animation-name: keyFrameScaleDown;
        animation-iteration-count: 1;
        animation-timing-function: ease-in;
        animation-duration: var(--paper-tooltip-duration-out, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .slide-down-animation {
        transform: translateY(-2000px);
        opacity: 0;
        animation-delay: var(--paper-tooltip-delay-out, 500ms);
        animation-name: keyFrameSlideDownIn;
        animation-iteration-count: 1;
        animation-timing-function: cubic-bezier(0.0, 0.0, 0.2, 1);
        animation-duration: var(--paper-tooltip-duration-out, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .slide-down-animation-out {
        transform: translateY(0);
        opacity: var(--paper-tooltip-opacity, 0.9);
        animation-delay: var(--paper-tooltip-delay-out, 500ms);
        animation-name: keyFrameSlideDownOut;
        animation-iteration-count: 1;
        animation-timing-function: cubic-bezier(0.4, 0.0, 1, 1);
        animation-duration: var(--paper-tooltip-duration-out, 500ms);
        animation-fill-mode: forwards;
        @apply --paper-tooltip-animation;
      }

      .cancel-animation {
        animation-delay: -30s !important;
      }

      /* Thanks IE 10. */

      .hidden {
        display: none !important;
      }
    </style>

    <div id="tooltip" class="hidden">
      <slot></slot>
    </div>
`,is:"paper-tooltip",hostAttributes:{role:"tooltip",tabindex:-1},properties:{for:{type:String,observer:"_findTarget"},manualMode:{type:Boolean,value:!1,observer:"_manualModeChanged"},position:{type:String,value:"bottom"},fitToVisibleBounds:{type:Boolean,value:!1},offset:{type:Number,value:14},marginTop:{type:Number,value:14},animationDelay:{type:Number,value:500,observer:"_delayChange"},animationEntry:{type:String,value:""},animationExit:{type:String,value:""},animationConfig:{type:Object,value:function(){return{entry:[{name:"fade-in-animation",node:this,timing:{delay:0}}],exit:[{name:"fade-out-animation",node:this}]}}},_showing:{type:Boolean,value:!1}},listeners:{webkitAnimationEnd:"_onAnimationEnd"},get target(){var t=(0,s.vz)(this).parentNode,i=(0,s.vz)(this).getOwnerRoot();return this.for?(0,s.vz)(i).querySelector("#"+this.for):t.nodeType==Node.DOCUMENT_FRAGMENT_NODE?i.host:t},attached:function(){this._findTarget()},detached:function(){this.manualMode||this._removeListeners()},playAnimation:function(t){"entry"===t?this.show():"exit"===t&&this.hide()},cancelAnimation:function(){this.$.tooltip.classList.add("cancel-animation")},show:function(){if(!this._showing){if(""===(0,s.vz)(this).textContent.trim()){for(var t=!0,i=(0,s.vz)(this).getEffectiveChildNodes(),e=0;e<i.length;e++)if(""!==i[e].textContent.trim()){t=!1;break}if(t)return}this._showing=!0,this.$.tooltip.classList.remove("hidden"),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.updatePosition(),this._animationPlaying=!0,this.$.tooltip.classList.add(this._getAnimationType("entry"))}},hide:function(){if(this._showing){if(this._animationPlaying)return this._showing=!1,void this._cancelAnimation();this._onAnimationFinish(),this._showing=!1,this._animationPlaying=!0}},updatePosition:function(){if(this._target&&this.offsetParent){var t=this.offset;14!=this.marginTop&&14==this.offset&&(t=this.marginTop);var i,e,n=this.offsetParent.getBoundingClientRect(),s=this._target.getBoundingClientRect(),o=this.getBoundingClientRect(),a=(s.width-o.width)/2,r=(s.height-o.height)/2,h=s.left-n.left,l=s.top-n.top;switch(this.position){case"top":i=h+a,e=l-o.height-t;break;case"bottom":i=h+a,e=l+s.height+t;break;case"left":i=h-o.width-t,e=l+r;break;case"right":i=h+s.width+t,e=l+r}this.fitToVisibleBounds?(n.left+i+o.width>window.innerWidth?(this.style.right="0px",this.style.left="auto"):(this.style.left=Math.max(0,i)+"px",this.style.right="auto"),n.top+e+o.height>window.innerHeight?(this.style.bottom=n.height-l+t+"px",this.style.top="auto"):(this.style.top=Math.max(-n.top,e)+"px",this.style.bottom="auto")):(this.style.left=i+"px",this.style.top=e+"px")}},_addListeners:function(){this._target&&(this.listen(this._target,"mouseenter","show"),this.listen(this._target,"focus","show"),this.listen(this._target,"mouseleave","hide"),this.listen(this._target,"blur","hide"),this.listen(this._target,"tap","hide")),this.listen(this.$.tooltip,"animationend","_onAnimationEnd"),this.listen(this,"mouseenter","hide")},_findTarget:function(){this.manualMode||this._removeListeners(),this._target=this.target,this.manualMode||this._addListeners()},_delayChange:function(t){500!==t&&this.updateStyles({"--paper-tooltip-delay-in":t+"ms"})},_manualModeChanged:function(){this.manualMode?this._removeListeners():this._addListeners()},_cancelAnimation:function(){this.$.tooltip.classList.remove(this._getAnimationType("entry")),this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.add("hidden")},_onAnimationFinish:function(){this._showing&&(this.$.tooltip.classList.remove(this._getAnimationType("entry")),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.add(this._getAnimationType("exit")))},_onAnimationEnd:function(){this._animationPlaying=!1,this._showing||(this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.$.tooltip.classList.add("hidden"))},_getAnimationType:function(t){if("entry"===t&&""!==this.animationEntry)return this.animationEntry;if("exit"===t&&""!==this.animationExit)return this.animationExit;if(this.animationConfig[t]&&"string"==typeof this.animationConfig[t][0].name){if(this.animationConfig[t][0].timing&&this.animationConfig[t][0].timing.delay&&0!==this.animationConfig[t][0].timing.delay){var i=this.animationConfig[t][0].timing.delay;"entry"===t?this.updateStyles({"--paper-tooltip-delay-in":i+"ms"}):"exit"===t&&this.updateStyles({"--paper-tooltip-delay-out":i+"ms"})}return this.animationConfig[t][0].name}},_removeListeners:function(){this._target&&(this.unlisten(this._target,"mouseenter","show"),this.unlisten(this._target,"focus","show"),this.unlisten(this._target,"mouseleave","hide"),this.unlisten(this._target,"blur","hide"),this.unlisten(this._target,"tap","hide")),this.unlisten(this.$.tooltip,"animationend","_onAnimationEnd"),this.unlisten(this,"mouseenter","hide")}})},21560:(t,i,e)=>{e.d(i,{ZH:()=>c,MT:()=>o,U2:()=>h,RV:()=>s,t8:()=>l});const n=function(){if(!(!navigator.userAgentData&&/Safari\//.test(navigator.userAgent)&&!/Chrom(e|ium)\//.test(navigator.userAgent))||!indexedDB.databases)return Promise.resolve();let t;return new Promise((i=>{const e=()=>indexedDB.databases().finally(i);t=setInterval(e,100),e()})).finally((()=>clearInterval(t)))};function s(t){return new Promise(((i,e)=>{t.oncomplete=t.onsuccess=()=>i(t.result),t.onabort=t.onerror=()=>e(t.error)}))}function o(t,i){const e=n().then((()=>{const e=indexedDB.open(t);return e.onupgradeneeded=()=>e.result.createObjectStore(i),s(e)}));return(t,n)=>e.then((e=>n(e.transaction(i,t).objectStore(i))))}let a;function r(){return a||(a=o("keyval-store","keyval")),a}function h(t,i=r()){return i("readonly",(i=>s(i.get(t))))}function l(t,i,e=r()){return e("readwrite",(e=>(e.put(i,t),s(e.transaction))))}function c(t=r()){return t("readwrite",(t=>(t.clear(),s(t.transaction))))}},14516:(t,i,e)=>{e.d(i,{Z:()=>o});var n=Number.isNaN||function(t){return"number"==typeof t&&t!=t};function s(t,i){if(t.length!==i.length)return!1;for(var e=0;e<t.length;e++)if(s=t[e],o=i[e],!(s===o||n(s)&&n(o)))return!1;var s,o;return!0}const o=function(t,i){var e;void 0===i&&(i=s);var n,o=[],a=!1;return function(){for(var s=[],r=0;r<arguments.length;r++)s[r]=arguments[r];return a&&e===this&&i(s,o)||(n=t.apply(this,s),a=!0,e=this,o=s),n}}},97330:(t,i,e)=>{e.d(i,{_:()=>s,B:()=>o});var n=e(43715);const s=(t,i,e,s)=>{if(t[i])return t[i];let o,a=0,r=(0,n.M)();const h=()=>e(t).then((t=>r.setState(t,!0))),l=()=>h().catch((i=>{if(t.connected)throw i}));return t[i]={get state(){return r.state},refresh:h,subscribe(i){a++,1===a&&(s&&(o=s(t,r)),t.addEventListener("ready",l),l());const e=r.subscribe(i);return void 0!==r.state&&setTimeout((()=>i(r.state)),0),()=>{e(),a--,a||(o&&o.then((t=>{t()})),t.removeEventListener("ready",h))}}},t[i]},o=(t,i,e,n,o)=>s(n,t,i,e).subscribe(o)},43715:(t,i,e)=>{e.d(i,{M:()=>n});const n=t=>{let i=[];function e(e,n){t=n?e:Object.assign(Object.assign({},t),e);let s=i;for(let i=0;i<s.length;i++)s[i](t)}return{get state(){return t},action(i){function n(t){e(t,!1)}return function(){let e=[t];for(let t=0;t<arguments.length;t++)e.push(arguments[t]);let s=i.apply(this,e);if(null!=s)return s instanceof Promise?s.then(n):n(s)}},setState:e,subscribe:t=>(i.push(t),()=>{!function(t){let e=[];for(let n=0;n<i.length;n++)i[n]===t?t=null:e.push(i[n]);i=e}(t)})}}},19596:(t,i,e)=>{e.d(i,{s:()=>d});var n=e(81563),s=e(38941);const o=(t,i)=>{var e,n;const s=t._$AN;if(void 0===s)return!1;for(const t of s)null===(n=(e=t)._$AO)||void 0===n||n.call(e,i,!1),o(t,i);return!0},a=t=>{let i,e;do{if(void 0===(i=t._$AM))break;e=i._$AN,e.delete(t),t=i}while(0===(null==e?void 0:e.size))},r=t=>{for(let i;i=t._$AM;t=i){let e=i._$AN;if(void 0===e)i._$AN=e=new Set;else if(e.has(t))break;e.add(t),c(i)}};function h(t){void 0!==this._$AN?(a(this),this._$AM=t,r(this)):this._$AM=t}function l(t,i=!1,e=0){const n=this._$AH,s=this._$AN;if(void 0!==s&&0!==s.size)if(i)if(Array.isArray(n))for(let t=e;t<n.length;t++)o(n[t],!1),a(n[t]);else null!=n&&(o(n,!1),a(n));else o(this,t)}const c=t=>{var i,e,n,o;t.type==s.pX.CHILD&&(null!==(i=(n=t)._$AP)&&void 0!==i||(n._$AP=l),null!==(e=(o=t)._$AQ)&&void 0!==e||(o._$AQ=h))};class d extends s.Xe{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,i,e){super._$AT(t,i,e),r(this),this.isConnected=t._$AU}_$AO(t,i=!0){var e,n;t!==this.isConnected&&(this.isConnected=t,t?null===(e=this.reconnected)||void 0===e||e.call(this):null===(n=this.disconnected)||void 0===n||n.call(this)),i&&(o(this,t),a(this))}setValue(t){if((0,n.OR)(this._$Ct))this._$Ct._$AI(t,this);else{const i=[...this._$Ct._$AH];i[this._$Ci]=t,this._$Ct._$AI(i,this,0)}}disconnected(){}reconnected(){}}},22142:(t,i,e)=>{e.d(i,{C:()=>d});var n=e(15304),s=e(38941),o=e(81563),a=e(19596);class r{constructor(t){this.U=t}disconnect(){this.U=void 0}reconnect(t){this.U=t}deref(){return this.U}}class h{constructor(){this.Y=void 0,this.q=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Y=this.q=void 0}}const l=t=>!(0,o.pt)(t)&&"function"==typeof t.then;class c extends a.s{constructor(){super(...arguments),this._$Cft=1073741823,this._$Cwt=[],this._$CG=new r(this),this._$CK=new h}render(...t){var i;return null!==(i=t.find((t=>!l(t))))&&void 0!==i?i:n.Jb}update(t,i){const e=this._$Cwt;let s=e.length;this._$Cwt=i;const o=this._$CG,a=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<i.length&&!(t>this._$Cft);t++){const n=i[t];if(!l(n))return this._$Cft=t,n;t<s&&n===e[t]||(this._$Cft=1073741823,s=0,Promise.resolve(n).then((async t=>{for(;a.get();)await a.get();const i=o.deref();if(void 0!==i){const e=i._$Cwt.indexOf(n);e>-1&&e<i._$Cft&&(i._$Cft=e,i.setValue(t))}})))}return n.Jb}disconnected(){this._$CG.disconnect(),this._$CK.pause()}reconnected(){this._$CG.reconnect(this),this._$CK.resume()}}const d=(0,s.XM)(c)}}]);
//# sourceMappingURL=fe8442ce.js.map