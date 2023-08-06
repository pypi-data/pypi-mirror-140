/*! For license information please see 7030e810.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[9357],{14166:(t,e,i)=>{i.d(e,{W:()=>o});var s=function(){return s=Object.assign||function(t){for(var e,i=1,s=arguments.length;i<s;i++)for(var o in e=arguments[i])Object.prototype.hasOwnProperty.call(e,o)&&(t[o]=e[o]);return t},s.apply(this,arguments)};function o(t,e,i){void 0===e&&(e=Date.now()),void 0===i&&(i={});var o=s(s({},a),i||{}),n=(+t-+e)/1e3;if(Math.abs(n)<o.second)return{value:Math.round(n),unit:"second"};var r=n/60;if(Math.abs(r)<o.minute)return{value:Math.round(r),unit:"minute"};var h=n/3600;if(Math.abs(h)<o.hour)return{value:Math.round(h),unit:"hour"};var l=n/86400;if(Math.abs(l)<o.day)return{value:Math.round(l),unit:"day"};var c=new Date(t),p=new Date(e),d=c.getFullYear()-p.getFullYear();if(Math.round(Math.abs(d))>0)return{value:Math.round(d),unit:"year"};var u=12*d+c.getMonth()-p.getMonth();if(Math.round(Math.abs(u))>0)return{value:Math.round(u),unit:"month"};var y=n/604800;return{value:Math.round(y),unit:"week"}}var a={second:45,minute:45,hour:22,day:5}},54040:(t,e,i)=>{var s=i(87480),o=i(33310),a=i(58417),n=i(39274);let r=class extends a.A{};r.styles=[n.W],r=(0,s.__decorate)([(0,o.Mo)("mwc-checkbox")],r)},56887:(t,e,i)=>{i.d(e,{F:()=>h});var s=i(87480),o=(i(54040),i(37500)),a=i(33310),n=i(8636),r=i(61092);class h extends r.K{constructor(){super(...arguments),this.left=!1,this.graphic="control"}render(){const t={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},e=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():o.dy``,s=this.hasMeta&&this.left?this.renderMeta():o.dy``,a=this.renderRipple();return o.dy`
      ${a}
      ${i}
      ${this.left?"":e}
      <span class=${(0,n.$)(t)}>
        <mwc-checkbox
            reducedTouchTarget
            tabindex=${this.tabindex}
            .checked=${this.selected}
            ?disabled=${this.disabled}
            @change=${this.onChange}>
        </mwc-checkbox>
      </span>
      ${this.left?e:""}
      ${s}`}async onChange(t){const e=t.target;this.selected===e.checked||(this._skipPropRequest=!0,this.selected=e.checked,await this.updateComplete,this._skipPropRequest=!1)}}(0,s.__decorate)([(0,a.IO)("slot")],h.prototype,"slotElement",void 0),(0,s.__decorate)([(0,a.IO)("mwc-checkbox")],h.prototype,"checkboxElement",void 0),(0,s.__decorate)([(0,a.Cb)({type:Boolean})],h.prototype,"left",void 0),(0,s.__decorate)([(0,a.Cb)({type:String,reflect:!0})],h.prototype,"graphic",void 0)},21270:(t,e,i)=>{i.d(e,{W:()=>s});const s=i(37500).iv`:host(:not([twoline])){height:56px}:host(:not([left])) .mdc-deprecated-list-item__meta{height:40px;width:40px}`},63207:(t,e,i)=>{i(65660),i(15112);var s=i(9672),o=i(87156),a=i(50856),n=i(48175);(0,s.k)({_template:a.d`
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
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:n.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(t){var e=(t||"").split(":");this._iconName=e.pop(),this._iconsetName=e.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(t){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,o.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,o.vz)(this.root).appendChild(this._img))}})},15112:(t,e,i)=>{i.d(e,{P:()=>o});i(48175);var s=i(9672);class o{constructor(t){o[" "](t),this.type=t&&t.type||"default",this.key=t&&t.key,t&&"value"in t&&(this.value=t.value)}get value(){var t=this.type,e=this.key;if(t&&e)return o.types[t]&&o.types[t][e]}set value(t){var e=this.type,i=this.key;e&&i&&(e=o.types[e]=o.types[e]||{},null==t?delete e[i]:e[i]=t)}get list(){if(this.type){var t=o.types[this.type];return t?Object.keys(t).map((function(t){return a[this.type][t]}),this):[]}}byKey(t){return this.key=t,this.value}}o[" "]=function(){},o.types={};var a=o.types;(0,s.k)({is:"iron-meta",properties:{type:{type:String,value:"default"},key:{type:String},value:{type:String,notify:!0},self:{type:Boolean,observer:"_selfChanged"},__meta:{type:Boolean,computed:"__computeMeta(type, key, value)"}},hostAttributes:{hidden:!0},__computeMeta:function(t,e,i){var s=new o({type:t,key:e});return void 0!==i&&i!==s.value?s.value=i:this.value!==s.value&&(this.value=s.value),s},get list(){return this.__meta&&this.__meta.list},_selfChanged:function(t){t&&(this.value=this)},byKey:function(t){return new o({type:this.type,key:t}).value}})},89194:(t,e,i)=>{i(48175),i(65660),i(70019);var s=i(9672),o=i(50856);(0,s.k)({_template:o.d`
    <style>
      :host {
        overflow: hidden; /* needed for text-overflow: ellipsis to work on ff */
        @apply --layout-vertical;
        @apply --layout-center-justified;
        @apply --layout-flex;
      }

      :host([two-line]) {
        min-height: var(--paper-item-body-two-line-min-height, 72px);
      }

      :host([three-line]) {
        min-height: var(--paper-item-body-three-line-min-height, 88px);
      }

      :host > ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      :host > ::slotted([secondary]) {
        @apply --paper-font-body1;

        color: var(--paper-item-body-secondary-color, var(--secondary-text-color));

        @apply --paper-item-body-secondary;
      }
    </style>

    <slot></slot>
`,is:"paper-item-body"})},53973:(t,e,i)=>{i(48175),i(65660),i(97968);var s=i(9672),o=i(50856),a=i(33760);(0,s.k)({_template:o.d`
    <style include="paper-item-shared-styles">
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
      }
    </style>
    <slot></slot>
`,is:"paper-item",behaviors:[a.U]})}}]);
//# sourceMappingURL=7030e810.js.map