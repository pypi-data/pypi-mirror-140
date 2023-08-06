/*! For license information please see 272d84c3.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[6606],{63207:(t,e,i)=>{i(65660),i(15112);var s=i(9672),n=i(87156),r=i(50856),o=i(48175);(0,s.k)({_template:r.d`
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
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:o.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(t){var e=(t||"").split(":");this._iconName=e.pop(),this._iconsetName=e.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(t){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,n.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,n.vz)(this.root).appendChild(this._img))}})},15112:(t,e,i)=>{i.d(e,{P:()=>n});i(48175);var s=i(9672);class n{constructor(t){n[" "](t),this.type=t&&t.type||"default",this.key=t&&t.key,t&&"value"in t&&(this.value=t.value)}get value(){var t=this.type,e=this.key;if(t&&e)return n.types[t]&&n.types[t][e]}set value(t){var e=this.type,i=this.key;e&&i&&(e=n.types[e]=n.types[e]||{},null==t?delete e[i]:e[i]=t)}get list(){if(this.type){var t=n.types[this.type];return t?Object.keys(t).map((function(t){return r[this.type][t]}),this):[]}}byKey(t){return this.key=t,this.value}}n[" "]=function(){},n.types={};var r=n.types;(0,s.k)({is:"iron-meta",properties:{type:{type:String,value:"default"},key:{type:String},value:{type:String,notify:!0},self:{type:Boolean,observer:"_selfChanged"},__meta:{type:Boolean,computed:"__computeMeta(type, key, value)"}},hostAttributes:{hidden:!0},__computeMeta:function(t,e,i){var s=new n({type:t,key:e});return void 0!==i&&i!==s.value?s.value=i:this.value!==s.value&&(this.value=s.value),s},get list(){return this.__meta&&this.__meta.list},_selfChanged:function(t){t&&(this.value=this)},byKey:function(t){return new n({type:this.type,key:t}).value}})},53973:(t,e,i)=>{i(48175),i(65660),i(97968);var s=i(9672),n=i(50856),r=i(33760);(0,s.k)({_template:n.d`
    <style include="paper-item-shared-styles">
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
      }
    </style>
    <slot></slot>
`,is:"paper-item",behaviors:[r.U]})},51095:(t,e,i)=>{i(48175);var s=i(98433),n=i(9672),r=i(50856);(0,n.k)({_template:r.d`
    <style>
      :host {
        display: block;
        padding: 8px 0;

        background: var(--paper-listbox-background-color, var(--primary-background-color));
        color: var(--paper-listbox-color, var(--primary-text-color));

        @apply --paper-listbox;
      }
    </style>

    <slot></slot>
`,is:"paper-listbox",behaviors:[s.i],hostAttributes:{role:"listbox"}})},21560:(t,e,i)=>{i.d(e,{ZH:()=>h,MT:()=>r,U2:()=>l,RV:()=>n,t8:()=>c});const s=function(){if(!(!navigator.userAgentData&&/Safari\//.test(navigator.userAgent)&&!/Chrom(e|ium)\//.test(navigator.userAgent))||!indexedDB.databases)return Promise.resolve();let t;return new Promise((e=>{const i=()=>indexedDB.databases().finally(e);t=setInterval(i,100),i()})).finally((()=>clearInterval(t)))};function n(t){return new Promise(((e,i)=>{t.oncomplete=t.onsuccess=()=>e(t.result),t.onabort=t.onerror=()=>i(t.error)}))}function r(t,e){const i=s().then((()=>{const i=indexedDB.open(t);return i.onupgradeneeded=()=>i.result.createObjectStore(e),n(i)}));return(t,s)=>i.then((i=>s(i.transaction(e,t).objectStore(e))))}let o;function a(){return o||(o=r("keyval-store","keyval")),o}function l(t,e=a()){return e("readonly",(e=>n(e.get(t))))}function c(t,e,i=a()){return i("readwrite",(i=>(i.put(e,t),n(i.transaction))))}function h(t=a()){return t("readwrite",(t=>(t.clear(),n(t.transaction))))}},57835:(t,e,i)=>{i.d(e,{Xe:()=>s.Xe,pX:()=>s.pX,XM:()=>s.XM});var s=i(38941)},1460:(t,e,i)=>{i.d(e,{l:()=>o});var s=i(15304),n=i(38941);const r={},o=(0,n.XM)(class extends n.Xe{constructor(){super(...arguments),this.nt=r}render(t,e){return e()}update(t,[e,i]){if(Array.isArray(e)){if(Array.isArray(this.nt)&&this.nt.length===e.length&&e.every(((t,e)=>t===this.nt[e])))return s.Jb}else if(this.nt===e)return s.Jb;return this.nt=Array.isArray(e)?Array.from(e):e,this.render(e,i)}})}}]);
//# sourceMappingURL=272d84c3.js.map