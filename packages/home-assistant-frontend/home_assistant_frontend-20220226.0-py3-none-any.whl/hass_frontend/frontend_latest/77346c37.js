/*! For license information please see 77346c37.js.LICENSE.txt */
(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[2554,1833,6734,6335],{18601:(i,e,t)=>{"use strict";t.d(e,{qN:()=>s.q,Wg:()=>c});var a,n,o=t(87480),r=t(33310),s=t(78220);const l=null!==(n=null===(a=window.ShadyDOM)||void 0===a?void 0:a.inUse)&&void 0!==n&&n;class c extends s.H{constructor(){super(...arguments),this.disabled=!1,this.containingForm=null,this.formDataListener=i=>{this.disabled||this.setFormData(i.formData)}}findFormElement(){if(!this.shadowRoot||l)return null;const i=this.getRootNode().querySelectorAll("form");for(const e of Array.from(i))if(e.contains(this))return e;return null}connectedCallback(){var i;super.connectedCallback(),this.containingForm=this.findFormElement(),null===(i=this.containingForm)||void 0===i||i.addEventListener("formdata",this.formDataListener)}disconnectedCallback(){var i;super.disconnectedCallback(),null===(i=this.containingForm)||void 0===i||i.removeEventListener("formdata",this.formDataListener),this.containingForm=null}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",(i=>{this.dispatchEvent(new Event("change",i))}))}}c.shadowRootOptions={mode:"open",delegatesFocus:!0},(0,o.__decorate)([(0,r.Cb)({type:Boolean})],c.prototype,"disabled",void 0)},14114:(i,e,t)=>{"use strict";t.d(e,{P:()=>a});const a=i=>(e,t)=>{if(e.constructor._observers){if(!e.constructor.hasOwnProperty("_observers")){const i=e.constructor._observers;e.constructor._observers=new Map,i.forEach(((i,t)=>e.constructor._observers.set(t,i)))}}else{e.constructor._observers=new Map;const i=e.updated;e.updated=function(e){i.call(this,e),e.forEach(((i,e)=>{const t=this.constructor._observers.get(e);void 0!==t&&t.call(this,this[e],i)}))}}e.constructor._observers.set(t,i)}},92685:(i,e,t)=>{"use strict";t.d(e,{a:()=>h});var a=t(87480),n=t(72774),o={ROOT:"mdc-form-field"},r={LABEL_SELECTOR:".mdc-form-field > label"};const s=function(i){function e(t){var n=i.call(this,(0,a.__assign)((0,a.__assign)({},e.defaultAdapter),t))||this;return n.click=function(){n.handleClick()},n}return(0,a.__extends)(e,i),Object.defineProperty(e,"cssClasses",{get:function(){return o},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return r},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},e.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},e.prototype.handleClick=function(){var i=this;this.adapter.activateInputRipple(),requestAnimationFrame((function(){i.adapter.deactivateInputRipple()}))},e}(n.K);var l=t(78220),c=t(18601),d=t(14114),u=t(37500),m=t(33310),p=t(8636);class h extends l.H{constructor(){super(...arguments),this.alignEnd=!1,this.spaceBetween=!1,this.nowrap=!1,this.label="",this.mdcFoundationClass=s}createAdapter(){return{registerInteractionHandler:(i,e)=>{this.labelEl.addEventListener(i,e)},deregisterInteractionHandler:(i,e)=>{this.labelEl.removeEventListener(i,e)},activateInputRipple:async()=>{const i=this.input;if(i instanceof c.Wg){const e=await i.ripple;e&&e.startPress()}},deactivateInputRipple:async()=>{const i=this.input;if(i instanceof c.Wg){const e=await i.ripple;e&&e.endPress()}}}}get input(){var i,e;return null!==(e=null===(i=this.slottedInputs)||void 0===i?void 0:i[0])&&void 0!==e?e:null}render(){const i={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return u.dy`
      <div class="mdc-form-field ${(0,p.$)(i)}">
        <slot></slot>
        <label class="mdc-label"
               @click="${this._labelClick}">${this.label}</label>
      </div>`}click(){this._labelClick()}_labelClick(){const i=this.input;i&&(i.focus(),i.click())}}(0,a.__decorate)([(0,m.Cb)({type:Boolean})],h.prototype,"alignEnd",void 0),(0,a.__decorate)([(0,m.Cb)({type:Boolean})],h.prototype,"spaceBetween",void 0),(0,a.__decorate)([(0,m.Cb)({type:Boolean})],h.prototype,"nowrap",void 0),(0,a.__decorate)([(0,m.Cb)({type:String}),(0,d.P)((async function(i){var e;null===(e=this.input)||void 0===e||e.setAttribute("aria-label",i)}))],h.prototype,"label",void 0),(0,a.__decorate)([(0,m.IO)(".mdc-form-field")],h.prototype,"mdcRoot",void 0),(0,a.__decorate)([(0,m.vZ)("",!0,"*")],h.prototype,"slottedInputs",void 0),(0,a.__decorate)([(0,m.IO)("label")],h.prototype,"labelEl",void 0)},92038:(i,e,t)=>{"use strict";t.d(e,{W:()=>a});const a=t(37500).iv`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{margin-left:auto;margin-right:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{margin-left:0;margin-right:auto}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}[dir=rtl] .mdc-form-field--space-between>label,.mdc-form-field--space-between>label[dir=rtl]{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87))}::slotted(mwc-switch){margin-right:10px}[dir=rtl] ::slotted(mwc-switch),::slotted(mwc-switch[dir=rtl]){margin-left:10px}`},8621:(i,e,t)=>{"use strict";t.d(e,{G:()=>f});t(48175);var a={"U+0008":"backspace","U+0009":"tab","U+001B":"esc","U+0020":"space","U+007F":"del"},n={8:"backspace",9:"tab",13:"enter",27:"esc",33:"pageup",34:"pagedown",35:"end",36:"home",32:"space",37:"left",38:"up",39:"right",40:"down",46:"del",106:"*"},o={shift:"shiftKey",ctrl:"ctrlKey",alt:"altKey",meta:"metaKey"},r=/[a-z0-9*]/,s=/U\+/,l=/^arrow/,c=/^space(bar)?/,d=/^escape$/;function u(i,e){var t="";if(i){var a=i.toLowerCase();" "===a||c.test(a)?t="space":d.test(a)?t="esc":1==a.length?e&&!r.test(a)||(t=a):t=l.test(a)?a.replace("arrow",""):"multiply"==a?"*":a}return t}function m(i,e){return i.key?u(i.key,e):i.detail&&i.detail.key?u(i.detail.key,e):(t=i.keyIdentifier,o="",t&&(t in a?o=a[t]:s.test(t)?(t=parseInt(t.replace("U+","0x"),16),o=String.fromCharCode(t).toLowerCase()):o=t.toLowerCase()),o||function(i){var e="";return Number(i)&&(e=i>=65&&i<=90?String.fromCharCode(32+i):i>=112&&i<=123?"f"+(i-112+1):i>=48&&i<=57?String(i-48):i>=96&&i<=105?String(i-96):n[i]),e}(i.keyCode)||"");var t,o}function p(i,e){return m(e,i.hasModifiers)===i.key&&(!i.hasModifiers||!!e.shiftKey==!!i.shiftKey&&!!e.ctrlKey==!!i.ctrlKey&&!!e.altKey==!!i.altKey&&!!e.metaKey==!!i.metaKey)}function h(i){return i.trim().split(" ").map((function(i){return function(i){return 1===i.length?{combo:i,key:i,event:"keydown"}:i.split("+").reduce((function(i,e){var t=e.split(":"),a=t[0],n=t[1];return a in o?(i[o[a]]=!0,i.hasModifiers=!0):(i.key=a,i.event=n||"keydown"),i}),{combo:i.split(":").shift()})}(i)}))}const f={properties:{keyEventTarget:{type:Object,value:function(){return this}},stopKeyboardEventPropagation:{type:Boolean,value:!1},_boundKeyHandlers:{type:Array,value:function(){return[]}},_imperativeKeyBindings:{type:Object,value:function(){return{}}}},observers:["_resetKeyEventListeners(keyEventTarget, _boundKeyHandlers)"],keyBindings:{},registered:function(){this._prepKeyBindings()},attached:function(){this._listenKeyEventListeners()},detached:function(){this._unlistenKeyEventListeners()},addOwnKeyBinding:function(i,e){this._imperativeKeyBindings[i]=e,this._prepKeyBindings(),this._resetKeyEventListeners()},removeOwnKeyBindings:function(){this._imperativeKeyBindings={},this._prepKeyBindings(),this._resetKeyEventListeners()},keyboardEventMatchesKeys:function(i,e){for(var t=h(e),a=0;a<t.length;++a)if(p(t[a],i))return!0;return!1},_collectKeyBindings:function(){var i=this.behaviors.map((function(i){return i.keyBindings}));return-1===i.indexOf(this.keyBindings)&&i.push(this.keyBindings),i},_prepKeyBindings:function(){for(var i in this._keyBindings={},this._collectKeyBindings().forEach((function(i){for(var e in i)this._addKeyBinding(e,i[e])}),this),this._imperativeKeyBindings)this._addKeyBinding(i,this._imperativeKeyBindings[i]);for(var e in this._keyBindings)this._keyBindings[e].sort((function(i,e){var t=i[0].hasModifiers;return t===e[0].hasModifiers?0:t?-1:1}))},_addKeyBinding:function(i,e){h(i).forEach((function(i){this._keyBindings[i.event]=this._keyBindings[i.event]||[],this._keyBindings[i.event].push([i,e])}),this)},_resetKeyEventListeners:function(){this._unlistenKeyEventListeners(),this.isAttached&&this._listenKeyEventListeners()},_listenKeyEventListeners:function(){this.keyEventTarget&&Object.keys(this._keyBindings).forEach((function(i){var e=this._keyBindings[i],t=this._onKeyBindingEvent.bind(this,e);this._boundKeyHandlers.push([this.keyEventTarget,i,t]),this.keyEventTarget.addEventListener(i,t)}),this)},_unlistenKeyEventListeners:function(){for(var i,e,t,a;this._boundKeyHandlers.length;)e=(i=this._boundKeyHandlers.pop())[0],t=i[1],a=i[2],e.removeEventListener(t,a)},_onKeyBindingEvent:function(i,e){if(this.stopKeyboardEventPropagation&&e.stopPropagation(),!e.defaultPrevented)for(var t=0;t<i.length;t++){var a=i[t][0],n=i[t][1];if(p(a,e)&&(this._triggerKeyHandler(a,n,e),e.defaultPrevented))return}},_triggerKeyHandler:function(i,e,t){var a=Object.create(i);a.keyboardEvent=t;var n=new CustomEvent(i.event,{detail:a,cancelable:!0});this[e].call(this,n),n.defaultPrevented&&t.preventDefault()}}},26110:(i,e,t)=>{"use strict";t.d(e,{a:()=>a});t(48175),t(87156);const a={properties:{focused:{type:Boolean,value:!1,notify:!0,readOnly:!0,reflectToAttribute:!0},disabled:{type:Boolean,value:!1,notify:!0,observer:"_disabledChanged",reflectToAttribute:!0},_oldTabIndex:{type:String},_boundFocusBlurHandler:{type:Function,value:function(){return this._focusBlurHandler.bind(this)}}},observers:["_changedControlState(focused, disabled)"],ready:function(){this.addEventListener("focus",this._boundFocusBlurHandler,!0),this.addEventListener("blur",this._boundFocusBlurHandler,!0)},_focusBlurHandler:function(i){this._setFocused("focus"===i.type)},_disabledChanged:function(i,e){this.setAttribute("aria-disabled",i?"true":"false"),this.style.pointerEvents=i?"none":"",i?(this._oldTabIndex=this.getAttribute("tabindex"),this._setFocused(!1),this.tabIndex=-1,this.blur()):void 0!==this._oldTabIndex&&(null===this._oldTabIndex?this.removeAttribute("tabindex"):this.setAttribute("tabindex",this._oldTabIndex))},_changedControlState:function(){this._controlStateChanged&&this._controlStateChanged()}}},15112:(i,e,t)=>{"use strict";t.d(e,{P:()=>n});t(48175);var a=t(9672);class n{constructor(i){n[" "](i),this.type=i&&i.type||"default",this.key=i&&i.key,i&&"value"in i&&(this.value=i.value)}get value(){var i=this.type,e=this.key;if(i&&e)return n.types[i]&&n.types[i][e]}set value(i){var e=this.type,t=this.key;e&&t&&(e=n.types[e]=n.types[e]||{},null==i?delete e[t]:e[t]=i)}get list(){if(this.type){var i=n.types[this.type];return i?Object.keys(i).map((function(i){return o[this.type][i]}),this):[]}}byKey(i){return this.key=i,this.value}}n[" "]=function(){},n.types={};var o=n.types;(0,a.k)({is:"iron-meta",properties:{type:{type:String,value:"default"},key:{type:String},value:{type:String,notify:!0},self:{type:Boolean,observer:"_selfChanged"},__meta:{type:Boolean,computed:"__computeMeta(type, key, value)"}},hostAttributes:{hidden:!0},__computeMeta:function(i,e,t){var a=new n({type:i,key:e});return void 0!==t&&t!==a.value?a.value=t:this.value!==a.value&&(this.value=a.value),a},get list(){return this.__meta&&this.__meta.list},_selfChanged:function(i){i&&(this.value=this)},byKey:function(i){return new n({type:this.type,key:i}).value}})},89194:(i,e,t)=>{"use strict";t(48175),t(65660),t(70019);var a=t(9672),n=t(50856);(0,a.k)({_template:n.d`
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
`,is:"paper-item-body"})},54444:(i,e,t)=>{"use strict";t(48175);var a=t(9672),n=t(87156),o=t(50856);(0,a.k)({_template:o.d`
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
`,is:"paper-tooltip",hostAttributes:{role:"tooltip",tabindex:-1},properties:{for:{type:String,observer:"_findTarget"},manualMode:{type:Boolean,value:!1,observer:"_manualModeChanged"},position:{type:String,value:"bottom"},fitToVisibleBounds:{type:Boolean,value:!1},offset:{type:Number,value:14},marginTop:{type:Number,value:14},animationDelay:{type:Number,value:500,observer:"_delayChange"},animationEntry:{type:String,value:""},animationExit:{type:String,value:""},animationConfig:{type:Object,value:function(){return{entry:[{name:"fade-in-animation",node:this,timing:{delay:0}}],exit:[{name:"fade-out-animation",node:this}]}}},_showing:{type:Boolean,value:!1}},listeners:{webkitAnimationEnd:"_onAnimationEnd"},get target(){var i=(0,n.vz)(this).parentNode,e=(0,n.vz)(this).getOwnerRoot();return this.for?(0,n.vz)(e).querySelector("#"+this.for):i.nodeType==Node.DOCUMENT_FRAGMENT_NODE?e.host:i},attached:function(){this._findTarget()},detached:function(){this.manualMode||this._removeListeners()},playAnimation:function(i){"entry"===i?this.show():"exit"===i&&this.hide()},cancelAnimation:function(){this.$.tooltip.classList.add("cancel-animation")},show:function(){if(!this._showing){if(""===(0,n.vz)(this).textContent.trim()){for(var i=!0,e=(0,n.vz)(this).getEffectiveChildNodes(),t=0;t<e.length;t++)if(""!==e[t].textContent.trim()){i=!1;break}if(i)return}this._showing=!0,this.$.tooltip.classList.remove("hidden"),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.updatePosition(),this._animationPlaying=!0,this.$.tooltip.classList.add(this._getAnimationType("entry"))}},hide:function(){if(this._showing){if(this._animationPlaying)return this._showing=!1,void this._cancelAnimation();this._onAnimationFinish(),this._showing=!1,this._animationPlaying=!0}},updatePosition:function(){if(this._target&&this.offsetParent){var i=this.offset;14!=this.marginTop&&14==this.offset&&(i=this.marginTop);var e,t,a=this.offsetParent.getBoundingClientRect(),n=this._target.getBoundingClientRect(),o=this.getBoundingClientRect(),r=(n.width-o.width)/2,s=(n.height-o.height)/2,l=n.left-a.left,c=n.top-a.top;switch(this.position){case"top":e=l+r,t=c-o.height-i;break;case"bottom":e=l+r,t=c+n.height+i;break;case"left":e=l-o.width-i,t=c+s;break;case"right":e=l+n.width+i,t=c+s}this.fitToVisibleBounds?(a.left+e+o.width>window.innerWidth?(this.style.right="0px",this.style.left="auto"):(this.style.left=Math.max(0,e)+"px",this.style.right="auto"),a.top+t+o.height>window.innerHeight?(this.style.bottom=a.height-c+i+"px",this.style.top="auto"):(this.style.top=Math.max(-a.top,t)+"px",this.style.bottom="auto")):(this.style.left=e+"px",this.style.top=t+"px")}},_addListeners:function(){this._target&&(this.listen(this._target,"mouseenter","show"),this.listen(this._target,"focus","show"),this.listen(this._target,"mouseleave","hide"),this.listen(this._target,"blur","hide"),this.listen(this._target,"tap","hide")),this.listen(this.$.tooltip,"animationend","_onAnimationEnd"),this.listen(this,"mouseenter","hide")},_findTarget:function(){this.manualMode||this._removeListeners(),this._target=this.target,this.manualMode||this._addListeners()},_delayChange:function(i){500!==i&&this.updateStyles({"--paper-tooltip-delay-in":i+"ms"})},_manualModeChanged:function(){this.manualMode?this._removeListeners():this._addListeners()},_cancelAnimation:function(){this.$.tooltip.classList.remove(this._getAnimationType("entry")),this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.add("hidden")},_onAnimationFinish:function(){this._showing&&(this.$.tooltip.classList.remove(this._getAnimationType("entry")),this.$.tooltip.classList.remove("cancel-animation"),this.$.tooltip.classList.add(this._getAnimationType("exit")))},_onAnimationEnd:function(){this._animationPlaying=!1,this._showing||(this.$.tooltip.classList.remove(this._getAnimationType("exit")),this.$.tooltip.classList.add("hidden"))},_getAnimationType:function(i){if("entry"===i&&""!==this.animationEntry)return this.animationEntry;if("exit"===i&&""!==this.animationExit)return this.animationExit;if(this.animationConfig[i]&&"string"==typeof this.animationConfig[i][0].name){if(this.animationConfig[i][0].timing&&this.animationConfig[i][0].timing.delay&&0!==this.animationConfig[i][0].timing.delay){var e=this.animationConfig[i][0].timing.delay;"entry"===i?this.updateStyles({"--paper-tooltip-delay-in":e+"ms"}):"exit"===i&&this.updateStyles({"--paper-tooltip-delay-out":e+"ms"})}return this.animationConfig[i][0].name}},_removeListeners:function(){this._target&&(this.unlisten(this._target,"mouseenter","show"),this.unlisten(this._target,"focus","show"),this.unlisten(this._target,"mouseleave","hide"),this.unlisten(this._target,"blur","hide"),this.unlisten(this._target,"tap","hide")),this.unlisten(this.$.tooltip,"animationend","_onAnimationEnd"),this.unlisten(this,"mouseenter","hide")}})},20122:(i,e,t)=>{i.exports=t(52461)},81563:(i,e,t)=>{"use strict";t.d(e,{E_:()=>f,i9:()=>p,_Y:()=>c,pt:()=>o,OR:()=>s,hN:()=>r,ws:()=>h,fk:()=>d,hl:()=>m});var a=t(15304);const{H:n}=a.Al,o=i=>null===i||"object"!=typeof i&&"function"!=typeof i,r=(i,e)=>{var t,a;return void 0===e?void 0!==(null===(t=i)||void 0===t?void 0:t._$litType$):(null===(a=i)||void 0===a?void 0:a._$litType$)===e},s=i=>void 0===i.strings,l=()=>document.createComment(""),c=(i,e,t)=>{var a;const o=i._$AA.parentNode,r=void 0===e?i._$AB:e._$AA;if(void 0===t){const e=o.insertBefore(l(),r),a=o.insertBefore(l(),r);t=new n(e,a,i,i.options)}else{const e=t._$AB.nextSibling,n=t._$AM,s=n!==i;if(s){let e;null===(a=t._$AQ)||void 0===a||a.call(t,i),t._$AM=i,void 0!==t._$AP&&(e=i._$AU)!==n._$AU&&t._$AP(e)}if(e!==r||s){let i=t._$AA;for(;i!==e;){const e=i.nextSibling;o.insertBefore(i,r),i=e}}}return t},d=(i,e,t=i)=>(i._$AI(e,t),i),u={},m=(i,e=u)=>i._$AH=e,p=i=>i._$AH,h=i=>{var e;null===(e=i._$AP)||void 0===e||e.call(i,!1,!0);let t=i._$AA;const a=i._$AB.nextSibling;for(;t!==a;){const i=t.nextSibling;t.remove(),t=i}},f=i=>{i._$AR()}},57835:(i,e,t)=>{"use strict";t.d(e,{Xe:()=>a.Xe,pX:()=>a.pX,XM:()=>a.XM});var a=t(38941)},52461:i=>{"use strict";i.exports=JSON.parse('{"Pacific/Niue":"(GMT-11:00) Niue","Pacific/Pago_Pago":"(GMT-11:00) Pago Pago","Pacific/Honolulu":"(GMT-10:00) Hawaii Time","Pacific/Rarotonga":"(GMT-10:00) Rarotonga","Pacific/Tahiti":"(GMT-10:00) Tahiti","Pacific/Marquesas":"(GMT-09:30) Marquesas","America/Anchorage":"(GMT-09:00) Alaska Time","Pacific/Gambier":"(GMT-09:00) Gambier","America/Los_Angeles":"(GMT-08:00) Pacific Time","America/Tijuana":"(GMT-08:00) Pacific Time - Tijuana","America/Vancouver":"(GMT-08:00) Pacific Time - Vancouver","America/Whitehorse":"(GMT-08:00) Pacific Time - Whitehorse","Pacific/Pitcairn":"(GMT-08:00) Pitcairn","America/Dawson_Creek":"(GMT-07:00) Mountain Time - Dawson Creek","America/Denver":"(GMT-07:00) Mountain Time","America/Edmonton":"(GMT-07:00) Mountain Time - Edmonton","America/Hermosillo":"(GMT-07:00) Mountain Time - Hermosillo","America/Mazatlan":"(GMT-07:00) Mountain Time - Chihuahua, Mazatlan","America/Phoenix":"(GMT-07:00) Mountain Time - Arizona","America/Yellowknife":"(GMT-07:00) Mountain Time - Yellowknife","America/Belize":"(GMT-06:00) Belize","America/Chicago":"(GMT-06:00) Central Time","America/Costa_Rica":"(GMT-06:00) Costa Rica","America/El_Salvador":"(GMT-06:00) El Salvador","America/Guatemala":"(GMT-06:00) Guatemala","America/Managua":"(GMT-06:00) Managua","America/Mexico_City":"(GMT-06:00) Central Time - Mexico City","America/Regina":"(GMT-06:00) Central Time - Regina","America/Tegucigalpa":"(GMT-06:00) Central Time - Tegucigalpa","America/Winnipeg":"(GMT-06:00) Central Time - Winnipeg","Pacific/Galapagos":"(GMT-06:00) Galapagos","America/Bogota":"(GMT-05:00) Bogota","America/Cancun":"(GMT-05:00) America Cancun","America/Cayman":"(GMT-05:00) Cayman","America/Guayaquil":"(GMT-05:00) Guayaquil","America/Havana":"(GMT-05:00) Havana","America/Iqaluit":"(GMT-05:00) Eastern Time - Iqaluit","America/Jamaica":"(GMT-05:00) Jamaica","America/Lima":"(GMT-05:00) Lima","America/Nassau":"(GMT-05:00) Nassau","America/New_York":"(GMT-05:00) Eastern Time","America/Panama":"(GMT-05:00) Panama","America/Port-au-Prince":"(GMT-05:00) Port-au-Prince","America/Rio_Branco":"(GMT-05:00) Rio Branco","America/Toronto":"(GMT-05:00) Eastern Time - Toronto","Pacific/Easter":"(GMT-05:00) Easter Island","America/Caracas":"(GMT-04:30) Caracas","America/Asuncion":"(GMT-03:00) Asuncion","America/Barbados":"(GMT-04:00) Barbados","America/Boa_Vista":"(GMT-04:00) Boa Vista","America/Campo_Grande":"(GMT-03:00) Campo Grande","America/Cuiaba":"(GMT-03:00) Cuiaba","America/Curacao":"(GMT-04:00) Curacao","America/Grand_Turk":"(GMT-04:00) Grand Turk","America/Guyana":"(GMT-04:00) Guyana","America/Halifax":"(GMT-04:00) Atlantic Time - Halifax","America/La_Paz":"(GMT-04:00) La Paz","America/Manaus":"(GMT-04:00) Manaus","America/Martinique":"(GMT-04:00) Martinique","America/Port_of_Spain":"(GMT-04:00) Port of Spain","America/Porto_Velho":"(GMT-04:00) Porto Velho","America/Puerto_Rico":"(GMT-04:00) Puerto Rico","America/Santo_Domingo":"(GMT-04:00) Santo Domingo","America/Thule":"(GMT-04:00) Thule","Atlantic/Bermuda":"(GMT-04:00) Bermuda","America/St_Johns":"(GMT-03:30) Newfoundland Time - St. Johns","America/Araguaina":"(GMT-03:00) Araguaina","America/Argentina/Buenos_Aires":"(GMT-03:00) Buenos Aires","America/Bahia":"(GMT-03:00) Salvador","America/Belem":"(GMT-03:00) Belem","America/Cayenne":"(GMT-03:00) Cayenne","America/Fortaleza":"(GMT-03:00) Fortaleza","America/Godthab":"(GMT-03:00) Godthab","America/Maceio":"(GMT-03:00) Maceio","America/Miquelon":"(GMT-03:00) Miquelon","America/Montevideo":"(GMT-03:00) Montevideo","America/Paramaribo":"(GMT-03:00) Paramaribo","America/Recife":"(GMT-03:00) Recife","America/Santiago":"(GMT-03:00) Santiago","America/Sao_Paulo":"(GMT-02:00) Sao Paulo","Antarctica/Palmer":"(GMT-03:00) Palmer","Antarctica/Rothera":"(GMT-03:00) Rothera","Atlantic/Stanley":"(GMT-03:00) Stanley","America/Noronha":"(GMT-02:00) Noronha","Atlantic/South_Georgia":"(GMT-02:00) South Georgia","America/Scoresbysund":"(GMT-01:00) Scoresbysund","Atlantic/Azores":"(GMT-01:00) Azores","Atlantic/Cape_Verde":"(GMT-01:00) Cape Verde","Africa/Abidjan":"(GMT+00:00) Abidjan","Africa/Accra":"(GMT+00:00) Accra","Africa/Bissau":"(GMT+00:00) Bissau","Africa/Casablanca":"(GMT+00:00) Casablanca","Africa/El_Aaiun":"(GMT+00:00) El Aaiun","Africa/Monrovia":"(GMT+00:00) Monrovia","America/Danmarkshavn":"(GMT+00:00) Danmarkshavn","Atlantic/Canary":"(GMT+00:00) Canary Islands","Atlantic/Faroe":"(GMT+00:00) Faeroe","Atlantic/Reykjavik":"(GMT+00:00) Reykjavik","Etc/GMT":"(GMT+00:00) GMT (no daylight saving)","Europe/Dublin":"(GMT+00:00) Dublin","Europe/Lisbon":"(GMT+00:00) Lisbon","Europe/London":"(GMT+00:00) London","Africa/Algiers":"(GMT+01:00) Algiers","Africa/Ceuta":"(GMT+01:00) Ceuta","Africa/Lagos":"(GMT+01:00) Lagos","Africa/Ndjamena":"(GMT+01:00) Ndjamena","Africa/Tunis":"(GMT+01:00) Tunis","Africa/Windhoek":"(GMT+02:00) Windhoek","Europe/Amsterdam":"(GMT+01:00) Amsterdam","Europe/Andorra":"(GMT+01:00) Andorra","Europe/Belgrade":"(GMT+01:00) Central European Time - Belgrade","Europe/Berlin":"(GMT+01:00) Berlin","Europe/Brussels":"(GMT+01:00) Brussels","Europe/Budapest":"(GMT+01:00) Budapest","Europe/Copenhagen":"(GMT+01:00) Copenhagen","Europe/Gibraltar":"(GMT+01:00) Gibraltar","Europe/Luxembourg":"(GMT+01:00) Luxembourg","Europe/Madrid":"(GMT+01:00) Madrid","Europe/Malta":"(GMT+01:00) Malta","Europe/Monaco":"(GMT+01:00) Monaco","Europe/Oslo":"(GMT+01:00) Oslo","Europe/Paris":"(GMT+01:00) Paris","Europe/Prague":"(GMT+01:00) Central European Time - Prague","Europe/Rome":"(GMT+01:00) Rome","Europe/Stockholm":"(GMT+01:00) Stockholm","Europe/Tirane":"(GMT+01:00) Tirane","Europe/Vienna":"(GMT+01:00) Vienna","Europe/Warsaw":"(GMT+01:00) Warsaw","Europe/Zurich":"(GMT+01:00) Zurich","Africa/Cairo":"(GMT+02:00) Cairo","Africa/Johannesburg":"(GMT+02:00) Johannesburg","Africa/Maputo":"(GMT+02:00) Maputo","Africa/Tripoli":"(GMT+02:00) Tripoli","Asia/Amman":"(GMT+02:00) Amman","Asia/Beirut":"(GMT+02:00) Beirut","Asia/Damascus":"(GMT+02:00) Damascus","Asia/Gaza":"(GMT+02:00) Gaza","Asia/Jerusalem":"(GMT+02:00) Jerusalem","Asia/Nicosia":"(GMT+02:00) Nicosia","Europe/Athens":"(GMT+02:00) Athens","Europe/Bucharest":"(GMT+02:00) Bucharest","Europe/Chisinau":"(GMT+02:00) Chisinau","Europe/Helsinki":"(GMT+02:00) Helsinki","Europe/Istanbul":"(GMT+02:00) Istanbul","Europe/Kaliningrad":"(GMT+02:00) Moscow-01 - Kaliningrad","Europe/Kiev":"(GMT+02:00) Kiev","Europe/Riga":"(GMT+02:00) Riga","Europe/Sofia":"(GMT+02:00) Sofia","Europe/Tallinn":"(GMT+02:00) Tallinn","Europe/Vilnius":"(GMT+02:00) Vilnius","Africa/Khartoum":"(GMT+03:00) Khartoum","Africa/Nairobi":"(GMT+03:00) Nairobi","Antarctica/Syowa":"(GMT+03:00) Syowa","Asia/Baghdad":"(GMT+03:00) Baghdad","Asia/Qatar":"(GMT+03:00) Qatar","Asia/Riyadh":"(GMT+03:00) Riyadh","Europe/Minsk":"(GMT+03:00) Minsk","Europe/Moscow":"(GMT+03:00) Moscow+00 - Moscow","Asia/Tehran":"(GMT+03:30) Tehran","Asia/Baku":"(GMT+04:00) Baku","Asia/Dubai":"(GMT+04:00) Dubai","Asia/Tbilisi":"(GMT+04:00) Tbilisi","Asia/Yerevan":"(GMT+04:00) Yerevan","Europe/Samara":"(GMT+04:00) Moscow+01 - Samara","Indian/Mahe":"(GMT+04:00) Mahe","Indian/Mauritius":"(GMT+04:00) Mauritius","Indian/Reunion":"(GMT+04:00) Reunion","Asia/Kabul":"(GMT+04:30) Kabul","Antarctica/Mawson":"(GMT+05:00) Mawson","Asia/Aqtau":"(GMT+05:00) Aqtau","Asia/Aqtobe":"(GMT+05:00) Aqtobe","Asia/Ashgabat":"(GMT+05:00) Ashgabat","Asia/Dushanbe":"(GMT+05:00) Dushanbe","Asia/Karachi":"(GMT+05:00) Karachi","Asia/Tashkent":"(GMT+05:00) Tashkent","Asia/Yekaterinburg":"(GMT+05:00) Moscow+02 - Yekaterinburg","Indian/Kerguelen":"(GMT+05:00) Kerguelen","Indian/Maldives":"(GMT+05:00) Maldives","Asia/Calcutta":"(GMT+05:30) India Standard Time","Asia/Colombo":"(GMT+05:30) Colombo","Asia/Katmandu":"(GMT+05:45) Katmandu","Antarctica/Vostok":"(GMT+06:00) Vostok","Asia/Almaty":"(GMT+06:00) Almaty","Asia/Bishkek":"(GMT+06:00) Bishkek","Asia/Dhaka":"(GMT+06:00) Dhaka","Asia/Omsk":"(GMT+06:00) Moscow+03 - Omsk, Novosibirsk","Asia/Thimphu":"(GMT+06:00) Thimphu","Indian/Chagos":"(GMT+06:00) Chagos","Asia/Rangoon":"(GMT+06:30) Rangoon","Indian/Cocos":"(GMT+06:30) Cocos","Antarctica/Davis":"(GMT+07:00) Davis","Asia/Bangkok":"(GMT+07:00) Bangkok","Asia/Hovd":"(GMT+07:00) Hovd","Asia/Jakarta":"(GMT+07:00) Jakarta","Asia/Krasnoyarsk":"(GMT+07:00) Moscow+04 - Krasnoyarsk","Asia/Saigon":"(GMT+07:00) Hanoi","Asia/Ho_Chi_Minh":"(GMT+07:00) Ho Chi Minh","Indian/Christmas":"(GMT+07:00) Christmas","Antarctica/Casey":"(GMT+08:00) Casey","Asia/Brunei":"(GMT+08:00) Brunei","Asia/Choibalsan":"(GMT+08:00) Choibalsan","Asia/Hong_Kong":"(GMT+08:00) Hong Kong","Asia/Irkutsk":"(GMT+08:00) Moscow+05 - Irkutsk","Asia/Kuala_Lumpur":"(GMT+08:00) Kuala Lumpur","Asia/Macau":"(GMT+08:00) Macau","Asia/Makassar":"(GMT+08:00) Makassar","Asia/Manila":"(GMT+08:00) Manila","Asia/Shanghai":"(GMT+08:00) China Time - Beijing","Asia/Singapore":"(GMT+08:00) Singapore","Asia/Taipei":"(GMT+08:00) Taipei","Asia/Ulaanbaatar":"(GMT+08:00) Ulaanbaatar","Australia/Perth":"(GMT+08:00) Western Time - Perth","Asia/Pyongyang":"(GMT+08:30) Pyongyang","Asia/Dili":"(GMT+09:00) Dili","Asia/Jayapura":"(GMT+09:00) Jayapura","Asia/Seoul":"(GMT+09:00) Seoul","Asia/Tokyo":"(GMT+09:00) Tokyo","Asia/Yakutsk":"(GMT+09:00) Moscow+06 - Yakutsk","Pacific/Palau":"(GMT+09:00) Palau","Australia/Adelaide":"(GMT+10:30) Central Time - Adelaide","Australia/Darwin":"(GMT+09:30) Central Time - Darwin","Antarctica/DumontDUrville":"(GMT+10:00) Dumont D\'Urville","Asia/Magadan":"(GMT+10:00) Moscow+07 - Magadan","Asia/Vladivostok":"(GMT+10:00) Moscow+07 - Yuzhno-Sakhalinsk","Australia/Brisbane":"(GMT+10:00) Eastern Time - Brisbane","Australia/Hobart":"(GMT+11:00) Eastern Time - Hobart","Australia/Sydney":"(GMT+11:00) Eastern Time - Melbourne, Sydney","Pacific/Chuuk":"(GMT+10:00) Truk","Pacific/Guam":"(GMT+10:00) Guam","Pacific/Port_Moresby":"(GMT+10:00) Port Moresby","Pacific/Efate":"(GMT+11:00) Efate","Pacific/Guadalcanal":"(GMT+11:00) Guadalcanal","Pacific/Kosrae":"(GMT+11:00) Kosrae","Pacific/Norfolk":"(GMT+11:00) Norfolk","Pacific/Noumea":"(GMT+11:00) Noumea","Pacific/Pohnpei":"(GMT+11:00) Ponape","Asia/Kamchatka":"(GMT+12:00) Moscow+09 - Petropavlovsk-Kamchatskiy","Pacific/Auckland":"(GMT+13:00) Auckland","Pacific/Fiji":"(GMT+13:00) Fiji","Pacific/Funafuti":"(GMT+12:00) Funafuti","Pacific/Kwajalein":"(GMT+12:00) Kwajalein","Pacific/Majuro":"(GMT+12:00) Majuro","Pacific/Nauru":"(GMT+12:00) Nauru","Pacific/Tarawa":"(GMT+12:00) Tarawa","Pacific/Wake":"(GMT+12:00) Wake","Pacific/Wallis":"(GMT+12:00) Wallis","Pacific/Apia":"(GMT+14:00) Apia","Pacific/Enderbury":"(GMT+13:00) Enderbury","Pacific/Fakaofo":"(GMT+13:00) Fakaofo","Pacific/Tongatapu":"(GMT+13:00) Tongatapu","Pacific/Kiritimati":"(GMT+14:00) Kiritimati"}')}}]);
//# sourceMappingURL=77346c37.js.map