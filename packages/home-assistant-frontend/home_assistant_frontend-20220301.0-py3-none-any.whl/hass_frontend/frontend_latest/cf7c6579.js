"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[6176],{60228:(e,t,r)=>{r.d(t,{j:()=>n});var i=r(7323);const n=(e,t)=>(a(t)||o(e,t))&&!s(e,t),o=(e,t)=>t.component?(0,i.p)(e,t.component):!t.components||t.components.some((t=>(0,i.p)(e,t))),a=e=>e.core,s=(e,t)=>(e=>e.advancedOnly)(t)&&!(e=>{var t;return null===(t=e.userData)||void 0===t?void 0:t.showAdvanced})(e)},96305:(e,t,r)=>{r.d(t,{v:()=>i});const i=(e,t)=>e&&Object.keys(e.services).filter((r=>t in e.services[r]))},27269:(e,t,r)=>{r.d(t,{p:()=>i});const i=e=>e.substr(e.indexOf(".")+1)},91741:(e,t,r)=>{r.d(t,{C:()=>n});var i=r(27269);const n=e=>void 0===e.attributes.friendly_name?(0,i.p)(e.entity_id).replace(/_/g," "):e.attributes.friendly_name||""},85415:(e,t,r)=>{r.d(t,{$:()=>i,f:()=>n});const i=(e,t)=>e<t?-1:e>t?1:0,n=(e,t)=>i(e.toLowerCase(),t.toLowerCase())},88324:(e,t,r)=>{var i=r(67182),n=r(37500),o=r(33310);function a(){a=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!c(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return u(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?u(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=h(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:p(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=p(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function s(e){var t,r=h(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function l(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function c(e){return e.decorators&&e.decorators.length}function d(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function p(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function h(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function u(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var n=a();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var p=t((function(e){n.initializeInstanceElements(e,h.elements)}),r),h=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(d(o.descriptor)||d(n.descriptor)){if(c(o)||c(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(c(o)){if(c(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}l(o,n)}else t.push(o)}return t}(p.d.map(s)),e);n.initializeClassElements(p.F,h.elements),n.runClassFinishers(p.F,h.finishers)}([(0,o.Mo)("ha-chip")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"hasIcon",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"noText",value:()=>!1},{kind:"method",key:"render",value:function(){return n.dy`
      <div class="mdc-chip ${this.noText?"no-text":""}">
        ${this.hasIcon?n.dy`<div class="mdc-chip__icon mdc-chip__icon--leading">
              <slot name="icon"></slot>
            </div>`:null}
        <div class="mdc-chip__ripple"></div>
        <span role="gridcell">
          <span role="button" tabindex="0" class="mdc-chip__primary-action">
            <span class="mdc-chip__text"><slot></slot></span>
          </span>
        </span>
      </div>
    `}},{kind:"get",static:!0,key:"styles",value:function(){return n.iv`
      ${(0,n.$m)(i)}
      .mdc-chip {
        background-color: var(
          --ha-chip-background-color,
          rgba(var(--rgb-primary-text-color), 0.15)
        );
        color: var(--ha-chip-text-color, var(--primary-text-color));
      }

      .mdc-chip.no-text {
        padding: 0 10px;
      }

      .mdc-chip:hover {
        color: var(--ha-chip-text-color, var(--primary-text-color));
      }

      .mdc-chip__icon--leading {
        --mdc-icon-size: 20px;
        color: var(--ha-chip-icon-color, var(--ha-chip-text-color));
      }
      .mdc-chip.no-text
        .mdc-chip__icon--leading:not(.mdc-chip__icon--leading-hidden) {
        margin-right: -4px;
      }
    `}}]}}),n.oi)},90806:(e,t,r)=>{var i=r(44636),n=r(37500);function o(){o=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!l(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return h(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?h(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=p(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:d(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=d(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function a(e){var t,r=p(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function s(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function l(e){return e.decorators&&e.decorators.length}function c(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function d(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function p(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function h(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var n=o();if(i)for(var d=0;d<i.length;d++)n=i[d](n);var p=t((function(e){n.initializeInstanceElements(e,h.elements)}),r),h=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(c(o.descriptor)||c(n.descriptor)){if(l(o)||l(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(l(o)){if(l(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}s(o,n)}else t.push(o)}return t}(p.d.map(a)),e);n.initializeClassElements(p.F,h.elements),n.runClassFinishers(p.F,h.finishers)}([(0,r(33310).Mo)("ha-header-bar")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"method",key:"render",value:function(){return n.dy`<header class="mdc-top-app-bar">
      <div class="mdc-top-app-bar__row">
        <section
          class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start"
          id="navigation"
        >
          <slot name="navigationIcon"></slot>
          <span class="mdc-top-app-bar__title">
            <slot name="title"></slot>
          </span>
        </section>
        <section
          class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end"
          id="actions"
          role="toolbar"
        >
          <slot name="actionItems"></slot>
        </section>
      </div>
    </header>`}},{kind:"get",static:!0,key:"styles",value:function(){return[(0,n.$m)(i),n.iv`
        .mdc-top-app-bar {
          position: static;
          color: var(--mdc-theme-on-primary, #fff);
        }
      `]}}]}}),n.oi)},3555:(e,t,r)=>{var i=r(86251),n=r(31338),o=r(37500),a=r(33310);function s(){s=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!d(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return f(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?f(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=u(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:h(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=h(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function l(e){var t,r=u(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function c(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function d(e){return e.decorators&&e.decorators.length}function p(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function h(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function u(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function f(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function m(e,t,r){return m="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=y(e)););return e}(e,t);if(i){var n=Object.getOwnPropertyDescriptor(i,t);return n.get?n.get.call(r):n.value}},m(e,t,r||e)}function y(e){return y=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},y(e)}!function(e,t,r,i){var n=s();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var a=t((function(e){n.initializeInstanceElements(e,h.elements)}),r),h=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(p(o.descriptor)||p(n.descriptor)){if(d(o)||d(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(d(o)){if(d(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}c(o,n)}else t.push(o)}return t}(a.d.map(l)),e);n.initializeClassElements(a.F,h.elements),n.runClassFinishers(a.F,h.finishers)}([(0,a.Mo)("ha-textfield")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,a.Cb)({type:Boolean})],key:"invalid",value:void 0},{kind:"field",decorators:[(0,a.Cb)({attribute:"error-message"})],key:"errorMessage",value:void 0},{kind:"method",key:"updated",value:function(e){m(y(r.prototype),"updated",this).call(this,e),(e.has("invalid")&&(this.invalid||void 0!==e.get("invalid"))||e.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||"Invalid":""),this.reportValidity())}},{kind:"method",key:"renderIcon",value:function(e,t=!1){const r=t?"trailing":"leading";return o.dy`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${r}"
        tabindex=${t?1:-1}
      >
        <slot name="${r}Icon"></slot>
      </span>
    `}},{kind:"field",static:!0,key:"styles",value:()=>[n.W,o.iv`
      .mdc-text-field__input {
        width: var(--ha-textfield-input-width, 100%);
      }
      .mdc-text-field:not(.mdc-text-field--with-leading-icon) {
        padding: var(--text-field-padding, 0px 16px);
      }
      .mdc-text-field__affix--suffix {
        padding-left: var(--text-field-suffix-padding-left, 12px);
        padding-right: var(--text-field-suffix-padding-right, 0px);
      }

      .mdc-text-field__icon {
        color: var(--secondary-text-color);
      }

      input {
        text-align: var(--text-field-text-align);
      }

      /* Chrome, Safari, Edge, Opera */
      :host([no-spinner]) input::-webkit-outer-spin-button,
      :host([no-spinner]) input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      /* Firefox */
      :host([no-spinner]) input[type="number"] {
        -moz-appearance: textfield;
      }

      .mdc-text-field__ripple {
        overflow: hidden;
      }

      .mdc-text-field {
        overflow: var(--text-field-overflow);
      }
    `]}]}}),i.P)},26765:(e,t,r)=>{r.d(t,{Ys:()=>a,g7:()=>s,D9:()=>l});var i=r(47181);const n=()=>Promise.all([r.e(9563),r.e(8985),r.e(5084),r.e(9588),r.e(1281)]).then(r.bind(r,1281)),o=(e,t,r)=>new Promise((o=>{const a=t.cancel,s=t.confirm;(0,i.B)(e,"show-dialog",{dialogTag:"dialog-box",dialogImport:n,dialogParams:{...t,...r,cancel:()=>{o(!(null==r||!r.prompt)&&null),a&&a()},confirm:e=>{o(null==r||!r.prompt||e),s&&s(e)}}})})),a=(e,t)=>o(e,t),s=(e,t)=>o(e,t,{confirmation:!0}),l=(e,t)=>o(e,t,{prompt:!0})},46176:(e,t,r)=>{r.r(t),r.d(t,{QuickBar:()=>U});r(9874),r(24103),r(44577);var i=r(37500),n=r(33310),o=r(51346),a=r(70483),s=r(14516),l=r(60228),c=r(96305),d=r(47181),p=r(58831),h=r(91741),u=r(16023),f=r(83849),m=r(85415);let y;!function(e){e[e.Null=0]="Null",e[e.Backspace=8]="Backspace",e[e.Tab=9]="Tab",e[e.LineFeed=10]="LineFeed",e[e.CarriageReturn=13]="CarriageReturn",e[e.Space=32]="Space",e[e.ExclamationMark=33]="ExclamationMark",e[e.DoubleQuote=34]="DoubleQuote",e[e.Hash=35]="Hash",e[e.DollarSign=36]="DollarSign",e[e.PercentSign=37]="PercentSign",e[e.Ampersand=38]="Ampersand",e[e.SingleQuote=39]="SingleQuote",e[e.OpenParen=40]="OpenParen",e[e.CloseParen=41]="CloseParen",e[e.Asterisk=42]="Asterisk",e[e.Plus=43]="Plus",e[e.Comma=44]="Comma",e[e.Dash=45]="Dash",e[e.Period=46]="Period",e[e.Slash=47]="Slash",e[e.Digit0=48]="Digit0",e[e.Digit1=49]="Digit1",e[e.Digit2=50]="Digit2",e[e.Digit3=51]="Digit3",e[e.Digit4=52]="Digit4",e[e.Digit5=53]="Digit5",e[e.Digit6=54]="Digit6",e[e.Digit7=55]="Digit7",e[e.Digit8=56]="Digit8",e[e.Digit9=57]="Digit9",e[e.Colon=58]="Colon",e[e.Semicolon=59]="Semicolon",e[e.LessThan=60]="LessThan",e[e.Equals=61]="Equals",e[e.GreaterThan=62]="GreaterThan",e[e.QuestionMark=63]="QuestionMark",e[e.AtSign=64]="AtSign",e[e.A=65]="A",e[e.B=66]="B",e[e.C=67]="C",e[e.D=68]="D",e[e.E=69]="E",e[e.F=70]="F",e[e.G=71]="G",e[e.H=72]="H",e[e.I=73]="I",e[e.J=74]="J",e[e.K=75]="K",e[e.L=76]="L",e[e.M=77]="M",e[e.N=78]="N",e[e.O=79]="O",e[e.P=80]="P",e[e.Q=81]="Q",e[e.R=82]="R",e[e.S=83]="S",e[e.T=84]="T",e[e.U=85]="U",e[e.V=86]="V",e[e.W=87]="W",e[e.X=88]="X",e[e.Y=89]="Y",e[e.Z=90]="Z",e[e.OpenSquareBracket=91]="OpenSquareBracket",e[e.Backslash=92]="Backslash",e[e.CloseSquareBracket=93]="CloseSquareBracket",e[e.Caret=94]="Caret",e[e.Underline=95]="Underline",e[e.BackTick=96]="BackTick",e[e.a=97]="a",e[e.b=98]="b",e[e.c=99]="c",e[e.d=100]="d",e[e.e=101]="e",e[e.f=102]="f",e[e.g=103]="g",e[e.h=104]="h",e[e.i=105]="i",e[e.j=106]="j",e[e.k=107]="k",e[e.l=108]="l",e[e.m=109]="m",e[e.n=110]="n",e[e.o=111]="o",e[e.p=112]="p",e[e.q=113]="q",e[e.r=114]="r",e[e.s=115]="s",e[e.t=116]="t",e[e.u=117]="u",e[e.v=118]="v",e[e.w=119]="w",e[e.x=120]="x",e[e.y=121]="y",e[e.z=122]="z",e[e.OpenCurlyBrace=123]="OpenCurlyBrace",e[e.Pipe=124]="Pipe",e[e.CloseCurlyBrace=125]="CloseCurlyBrace",e[e.Tilde=126]="Tilde"}(y||(y={}));const v=128;function g(){const e=[],t=[];for(let e=0;e<=v;e++)t[e]=0;for(let r=0;r<=v;r++)e.push(t.slice(0));return e}function k(e,t){if(t<0||t>=e.length)return!1;const r=e.codePointAt(t);switch(r){case y.Underline:case y.Dash:case y.Period:case y.Space:case y.Slash:case y.Backslash:case y.SingleQuote:case y.DoubleQuote:case y.Colon:case y.DollarSign:case y.LessThan:case y.OpenParen:case y.OpenSquareBracket:return!0;case void 0:return!1;default:return(i=r)>=127462&&i<=127487||8986===i||8987===i||9200===i||9203===i||i>=9728&&i<=10175||11088===i||11093===i||i>=127744&&i<=128591||i>=128640&&i<=128764||i>=128992&&i<=129003||i>=129280&&i<=129535||i>=129648&&i<=129750?!0:!1}var i}function b(e,t){if(t<0||t>=e.length)return!1;switch(e.charCodeAt(t)){case y.Space:case y.Tab:return!0;default:return!1}}function w(e,t,r){return t[e]!==r[e]}var _;function E(e,t,r,i,n,o,a){const s=e.length>v?v:e.length,l=i.length>v?v:i.length;if(r>=s||o>=l||s-r>l-o)return;if(!function(e,t,r,i,n,o,a=!1){for(;t<r&&n<o;)e[t]===i[n]&&(a&&(C[t]=n),t+=1),n+=1;return t===r}(t,r,s,n,o,l,!0))return;let c;!function(e,t,r,i,n,o){let a=e-1,s=t-1;for(;a>=r&&s>=i;)n[a]===o[s]&&(A[a]=s,a--),s--}(s,l,r,o,t,n);let d,p,h=1;const u=[!1];for(c=1,d=r;d<s;c++,d++){const a=C[d],f=A[d],m=d+1<s?A[d+1]:l;for(h=a-o+1,p=a;p<m;h++,p++){let s=Number.MIN_SAFE_INTEGER,m=!1;p<=f&&(s=x(e,t,d,r,i,n,p,l,o,0===D[c-1][h-1],u));let y=0;s!==Number.MAX_SAFE_INTEGER&&(m=!0,y=s+P[c-1][h-1]);const v=p>a,g=v?P[c][h-1]+(D[c][h-1]>0?-5:0):0,k=p>a+1&&D[c][h-1]>0,b=k?P[c][h-2]+(D[c][h-2]>0?-5:0):0;if(k&&(!v||b>=g)&&(!m||b>=y))P[c][h]=b,S[c][h]=_.LeftLeft,D[c][h]=0;else if(v&&(!m||g>=y))P[c][h]=g,S[c][h]=_.Left,D[c][h]=0;else{if(!m)throw new Error("not possible");P[c][h]=y,S[c][h]=_.Diag,D[c][h]=D[c-1][h-1]+1}}}if(!u[0]&&!a)return;c--,h--;const f=[P[c][h],o];let m=0,y=0;for(;c>=1;){let e=h;do{const t=S[c][e];if(t===_.LeftLeft)e-=2;else{if(t!==_.Left)break;e-=1}}while(e>=1);m>1&&t[r+c-1]===n[o+h-1]&&!w(e+o-1,i,n)&&m+1>D[c][e]&&(e=h),e===h?m++:m=1,y||(y=e),c--,h=e-1,f.push(h)}l===s&&(f[0]+=2);const g=y-s;return f[0]-=g,f}function x(e,t,r,i,n,o,a,s,l,c,d){if(t[r]!==o[a])return Number.MIN_SAFE_INTEGER;let p=1,h=!1;return a===r-i?p=e[r]===n[a]?7:5:!w(a,n,o)||0!==a&&w(a-1,n,o)?!k(o,a)||0!==a&&k(o,a-1)?(k(o,a-1)||b(o,a-1))&&(p=5,h=!0):p=5:(p=e[r]===n[a]?7:5,h=!0),p>1&&r===i&&(d[0]=!0),h||(h=w(a,n,o)||k(o,a-1)||b(o,a-1)),r===i?a>l&&(p-=h?3:5):p+=c?h?2:0:h?0:1,a+1===s&&(p-=h?3:5),p}!function(e){e[e.Diag=1]="Diag",e[e.Left=2]="Left",e[e.LeftLeft=3]="LeftLeft"}(_||(_={}));const C=T(256),A=T(256),D=g(),P=g(),S=g();function T(e){const t=[];for(let r=0;r<=e;r++)t[r]=0;return t}const I=(e,t)=>t.map((t=>(t.score=((e,t)=>{let r=Number.NEGATIVE_INFINITY;for(const i of t.strings){const t=E(e,e.toLowerCase(),0,i,i.toLowerCase(),0,!0);if(!t)continue;const n=0===t[0]?1:t[0];n>r&&(r=n)}if(r!==Number.NEGATIVE_INFINITY)return r})(e,t),t))).filter((e=>void 0!==e.score)).sort((({score:e=0},{score:t=0})=>e>t?-1:e<t?1:0));var z=r(38346),$=(r(88324),r(31206),r(90806),r(10983),r(3555),r(5986)),O=r(1887),L=r(29311),F=r(11654),j=r(26765);function M(){M=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!B(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return K(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?K(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=R(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:q(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=q(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function N(e){var t,r=R(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function H(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function B(e){return e.decorators&&e.decorators.length}function V(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function q(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function R(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function K(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}const Q="M2 12C2 16.97 6.03 21 11 21C13.39 21 15.68 20.06 17.4 18.4L15.9 16.9C14.63 18.25 12.86 19 11 19C4.76 19 1.64 11.46 6.05 7.05C10.46 2.64 18 5.77 18 12H15L19 16H19.1L23 12H20C20 7.03 15.97 3 11 3C6.03 3 2 7.03 2 12Z";let U=function(e,t,r,i){var n=M();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var a=t((function(e){n.initializeInstanceElements(e,s.elements)}),r),s=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(V(o.descriptor)||V(n.descriptor)){if(B(o)||B(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(B(o)){if(B(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}H(o,n)}else t.push(o)}return t}(a.d.map(N)),e);return n.initializeClassElements(a.F,s.elements),n.runClassFinishers(a.F,s.finishers)}([(0,n.Mo)("ha-quick-bar")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_commandItems",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_entityItems",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_filter",value:()=>""},{kind:"field",decorators:[(0,n.SB)()],key:"_search",value:()=>""},{kind:"field",decorators:[(0,n.SB)()],key:"_opened",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_commandMode",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_done",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_narrow",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_hint",value:void 0},{kind:"field",decorators:[(0,n.IO)("ha-textfield",!1)],key:"_filterInputField",value:void 0},{kind:"field",key:"_focusSet",value:()=>!1},{kind:"field",key:"_focusListElement",value:void 0},{kind:"method",key:"showDialog",value:async function(e){this._commandMode=e.commandMode||this._toggleIfAlreadyOpened(),this._hint=e.hint,this._narrow=matchMedia("all and (max-width: 450px), all and (max-height: 500px)").matches,this._initializeItemsIfNeeded(),this._opened=!0}},{kind:"method",key:"closeDialog",value:function(){this._opened=!1,this._done=!1,this._focusSet=!1,this._filter="",this._search="",(0,d.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"field",key:"_getItems",value(){return(0,s.Z)(((e,t,r,i)=>{const n=e?t:r;return n&&i&&" "!==i?this._filterItems(n,i):n}))}},{kind:"method",key:"render",value:function(){if(!this._opened)return i.dy``;const e=this._getItems(this._commandMode,this._commandItems,this._entityItems,this._filter);return i.dy`
      <ha-dialog
        .heading=${this.hass.localize("ui.dialogs.quick-bar.title")}
        open
        @opened=${this._handleOpened}
        @closed=${this.closeDialog}
        hideActions
      >
        <div slot="heading" class="heading">
          <ha-textfield
            dialogInitialFocus
            .placeholder=${this.hass.localize("ui.dialogs.quick-bar.filter_placeholder")}
            aria-label=${this.hass.localize("ui.dialogs.quick-bar.filter_placeholder")}
            .value=${this._commandMode?`>${this._search}`:this._search}
            .icon=${!0}
            .iconTrailing=${void 0!==this._search||this._narrow}
            @input=${this._handleSearchChange}
            @keydown=${this._handleInputKeyDown}
            @focus=${this._setFocusFirstListItem}
          >
            ${this._commandMode?i.dy`
                  <ha-svg-icon
                    slot="leadingIcon"
                    class="prefix"
                    .path=${"M13,19V16H21V19H13M8.5,13L2.47,7H6.71L11.67,11.95C12.25,12.54 12.25,13.5 11.67,14.07L6.74,19H2.5L8.5,13Z"}
                  ></ha-svg-icon>
                `:i.dy`
                  <ha-svg-icon
                    slot="leadingIcon"
                    class="prefix"
                    .path=${"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"}
                  ></ha-svg-icon>
                `}
            ${this._search||this._narrow?i.dy`
                  <div slot="trailingIcon">
                    ${this._search&&i.dy`<ha-icon-button
                      @click=${this._clearSearch}
                      .label=${this.hass.localize("ui.common.clear")}
                      .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                    ></ha-icon-button>`}
                    ${this._narrow?i.dy`
                          <mwc-button
                            .label=${this.hass.localize("ui.common.close")}
                            @click=${this.closeDialog}
                          ></mwc-button>
                        `:""}
                  </div>
                `:""}
          </ha-textfield>
        </div>
        ${e?0===e.length?i.dy`
              <div class="nothing-found">
                ${this.hass.localize("ui.dialogs.quick-bar.nothing_found")}
              </div>
            `:i.dy`
              <mwc-list>
                <lit-virtualizer
                  scroller
                  @keydown=${this._handleListItemKeyDown}
                  @rangechange=${this._handleRangeChanged}
                  @click=${this._handleItemClick}
                  class="ha-scrollbar"
                  style=${(0,a.V)({height:this._narrow?"calc(100vh - 56px)":`${Math.min(e.length*(this._commandMode?56:72)+26,this._done?500:0)}px`})}
                  .items=${e}
                  .renderItem=${this._renderItem}
                >
                </lit-virtualizer>
              </mwc-list>
            `:i.dy`<ha-circular-progress
              size="small"
              active
            ></ha-circular-progress>`}
        ${this._hint?i.dy`<div class="hint">${this._hint}</div>`:""}
      </ha-dialog>
    `}},{kind:"method",key:"_initializeItemsIfNeeded",value:function(){this._commandMode?this._commandItems=this._commandItems||this._generateCommandItems():this._entityItems=this._entityItems||this._generateEntityItems()}},{kind:"method",key:"_handleOpened",value:function(){this.updateComplete.then((()=>{this._done=!0}))}},{kind:"method",key:"_handleRangeChanged",value:async function(e){this._focusSet||e.firstVisible>-1&&(this._focusSet=!0,await this.updateComplete,this._setFocusFirstListItem())}},{kind:"field",key:"_renderItem",value(){return(e,t)=>e?(e=>void 0!==e.categoryKey)(e)?this._renderCommandItem(e,t):this._renderEntityItem(e,t):i.dy``}},{kind:"method",key:"_renderEntityItem",value:function(e,t){return i.dy`
      <mwc-list-item
        .twoline=${Boolean(e.altText)}
        .item=${e}
        index=${(0,o.o)(t)}
        graphic="icon"
      >
        ${e.iconPath?i.dy`<ha-svg-icon
              .path=${e.iconPath}
              class="entity"
              slot="graphic"
            ></ha-svg-icon>`:i.dy`<ha-icon
              .icon=${e.icon}
              class="entity"
              slot="graphic"
            ></ha-icon>`}
        <span>${e.primaryText}</span>
        ${e.altText?i.dy`
              <span slot="secondary" class="item-text secondary"
                >${e.altText}</span
              >
            `:null}
      </mwc-list-item>
    `}},{kind:"method",key:"_renderCommandItem",value:function(e,t){return i.dy`
      <mwc-list-item
        .item=${e}
        index=${(0,o.o)(t)}
        class="command-item"
        hasMeta
      >
        <span>
          <ha-chip
            .label=${e.categoryText}
            hasIcon
            class="command-category ${e.categoryKey}"
          >
            ${e.iconPath?i.dy`<ha-svg-icon
                  .path=${e.iconPath}
                  slot="icon"
                ></ha-svg-icon>`:""}
            ${e.categoryText}</ha-chip
          >
        </span>

        <span class="command-text">${e.primaryText}</span>
      </mwc-list-item>
    `}},{kind:"method",key:"processItemAndCloseDialog",value:async function(e,t){this._addSpinnerToCommandItem(t),await e.action(),this.closeDialog()}},{kind:"method",key:"_handleInputKeyDown",value:function(e){if("Enter"===e.code){const e=this._getItemAtIndex(0);if(!e||"none"===e.style.display)return;this.processItemAndCloseDialog(e.item,0)}else if("ArrowDown"===e.code){var t;e.preventDefault(),null===(t=this._getItemAtIndex(0))||void 0===t||t.focus(),this._focusSet=!0,this._focusListElement=this._getItemAtIndex(0)}}},{kind:"method",key:"_getItemAtIndex",value:function(e){return this.renderRoot.querySelector(`mwc-list-item[index="${e}"]`)}},{kind:"method",key:"_addSpinnerToCommandItem",value:function(e){var t;const r=document.createElement("ha-circular-progress");r.size="small",r.slot="meta",r.active=!0,null===(t=this._getItemAtIndex(e))||void 0===t||t.appendChild(r)}},{kind:"method",key:"_handleSearchChange",value:function(e){const t=e.currentTarget.value,r=this._commandMode,i=this._search;let n,o;t.startsWith(">")?(n=!0,o=t.substring(1)):(n=!1,o=t),r===n&&i===o||(this._commandMode=n,this._search=o,this._hint&&(this._hint=void 0),r!==this._commandMode?(this._focusSet=!1,this._initializeItemsIfNeeded(),this._filter=this._search):(this._focusSet&&this._focusListElement&&(this._focusSet=!1,this._focusListElement.rippleHandlers.endFocus()),this._debouncedSetFilter(this._search)))}},{kind:"method",key:"_clearSearch",value:function(){this._search="",this._filter=""}},{kind:"field",key:"_debouncedSetFilter",value(){return(0,z.D)((e=>{this._filter=e}),100)}},{kind:"method",key:"_setFocusFirstListItem",value:function(){var e;null===(e=this._getItemAtIndex(0))||void 0===e||e.rippleHandlers.startFocus(),this._focusListElement=this._getItemAtIndex(0)}},{kind:"method",key:"_handleListItemKeyDown",value:function(e){const t=1===e.key.length,r=e.target.getAttribute("index"),i="0"===r;var n,o,a,s;(this._focusListElement=e.target,"ArrowDown"===e.key)&&(null===(n=this._getItemAtIndex(Number(r)+1))||void 0===n||n.focus());"ArrowUp"===e.key&&(i?null===(o=this._filterInputField)||void 0===o||o.focus():null===(a=this._getItemAtIndex(Number(r)-1))||void 0===a||a.focus());("Enter"!==e.key&&" "!==e.key||this.processItemAndCloseDialog(e.target.item,Number(e.target.getAttribute("index"))),"Backspace"===e.key||t)&&(e.currentTarget.scrollTop=0,null===(s=this._filterInputField)||void 0===s||s.focus())}},{kind:"method",key:"_handleItemClick",value:function(e){this.processItemAndCloseDialog(e.target.item,Number(e.target.getAttribute("index")))}},{kind:"method",key:"_generateEntityItems",value:function(){return Object.keys(this.hass.states).map((e=>{const t=this.hass.states[e],r={primaryText:(0,h.C)(t),altText:e,icon:t.attributes.icon,iconPath:t.attributes.icon?void 0:(0,u.K)((0,p.M)(e),t),action:()=>(0,d.B)(this,"hass-more-info",{entityId:e})};return{...r,strings:[r.primaryText,r.altText]}})).sort(((e,t)=>(0,m.f)(e.primaryText,t.primaryText)))}},{kind:"method",key:"_generateCommandItems",value:function(){return[...this._generateReloadCommands(),...this._generateServerControlCommands(),...this._generateNavigationCommands()].sort(((e,t)=>(0,m.f)(e.strings.join(" "),t.strings.join(" "))))}},{kind:"method",key:"_generateReloadCommands",value:function(){const e=(0,c.v)(this.hass,"reload").map((e=>({primaryText:this.hass.localize(`ui.dialogs.quick-bar.commands.reload.${e}`)||this.hass.localize("ui.dialogs.quick-bar.commands.reload.reload","domain",(0,$.Lh)(this.hass.localize,e)),action:()=>this.hass.callService(e,"reload"),iconPath:Q,categoryText:this.hass.localize("ui.dialogs.quick-bar.commands.types.reload")})));return e.push({primaryText:this.hass.localize("ui.dialogs.quick-bar.commands.reload.themes"),action:()=>this.hass.callService("frontend","reload_themes"),iconPath:Q,categoryText:this.hass.localize("ui.dialogs.quick-bar.commands.types.reload")}),e.push({primaryText:this.hass.localize("ui.dialogs.quick-bar.commands.reload.core"),action:()=>this.hass.callService("homeassistant","reload_core_config"),iconPath:Q,categoryText:this.hass.localize("ui.dialogs.quick-bar.commands.types.reload")}),e.map((e=>({...e,categoryKey:"reload",strings:[`${e.categoryText} ${e.primaryText}`]})))}},{kind:"method",key:"_generateServerControlCommands",value:function(){return["restart","stop"].map((e=>{const t="server_control",r={primaryText:this.hass.localize("ui.dialogs.quick-bar.commands.server_control.perform_action","action",this.hass.localize(`ui.dialogs.quick-bar.commands.server_control.${e}`)),iconPath:"M13,19H14A1,1 0 0,1 15,20H22V22H15A1,1 0 0,1 14,23H10A1,1 0 0,1 9,22H2V20H9A1,1 0 0,1 10,19H11V17H4A1,1 0 0,1 3,16V12A1,1 0 0,1 4,11H20A1,1 0 0,1 21,12V16A1,1 0 0,1 20,17H13V19M4,3H20A1,1 0 0,1 21,4V8A1,1 0 0,1 20,9H4A1,1 0 0,1 3,8V4A1,1 0 0,1 4,3M9,7H10V5H9V7M9,15H10V13H9V15M5,5V7H7V5H5M5,13V15H7V13H5Z",categoryText:this.hass.localize("ui.dialogs.quick-bar.commands.types.server_control"),categoryKey:t,action:()=>this.hass.callService("homeassistant",e)};return this._generateConfirmationCommand({...r,strings:[`${r.categoryText} ${r.primaryText}`]},this.hass.localize("ui.dialogs.generic.ok"))}))}},{kind:"method",key:"_generateNavigationCommands",value:function(){const e=this._generateNavigationPanelCommands(),t=this._generateNavigationConfigSectionCommands();return this._finalizeNavigationCommands([...e,...t])}},{kind:"method",key:"_generateNavigationPanelCommands",value:function(){return Object.keys(this.hass.panels).filter((e=>"_my_redirect"!==e)).map((e=>{const t=this.hass.panels[e],r=(0,O.ct)(t);return{primaryText:this.hass.localize(r)||t.title||t.url_path,path:`/${t.url_path}`}}))}},{kind:"method",key:"_generateNavigationConfigSectionCommands",value:function(){const e=[];for(const t of Object.keys(L.configSections))for(const r of L.configSections[t]){if(!(0,l.j)(this.hass,r))continue;if(!r.component)continue;const t=this._getNavigationInfoFromConfig(r);t&&(e.some((e=>e.path===t.path&&e.component===t.component))||e.push(t))}return e}},{kind:"method",key:"_getNavigationInfoFromConfig",value:function(e){if(!e.component)return;const t=this.hass.localize(`ui.dialogs.quick-bar.commands.navigation.${e.component}`);return e.translationKey&&t?{...e,primaryText:t}:void 0}},{kind:"method",key:"_generateConfirmationCommand",value:function(e,t){return{...e,action:()=>(0,j.g7)(this,{confirmText:t,confirm:e.action})}}},{kind:"method",key:"_finalizeNavigationCommands",value:function(e){return e.map((e=>{const t="navigation",r={...e,iconPath:"M17.9,17.39C17.64,16.59 16.89,16 16,16H15V13A1,1 0 0,0 14,12H8V10H10A1,1 0 0,0 11,9V7H13A2,2 0 0,0 15,5V4.59C17.93,5.77 20,8.64 20,12C20,14.08 19.2,15.97 17.9,17.39M11,19.93C7.05,19.44 4,16.08 4,12C4,11.38 4.08,10.78 4.21,10.21L9,15V16A2,2 0 0,0 11,18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z",categoryText:this.hass.localize("ui.dialogs.quick-bar.commands.types.navigation"),action:()=>(0,f.c)(e.path)};return{...r,strings:[`${r.categoryText} ${r.primaryText}`],categoryKey:t}}))}},{kind:"method",key:"_toggleIfAlreadyOpened",value:function(){return!!this._opened&&!this._commandMode}},{kind:"field",key:"_filterItems",value:()=>(0,s.Z)(((e,t)=>I(t.trimLeft(),e)))},{kind:"get",static:!0,key:"styles",value:function(){return[F.$c,F.yu,i.iv`
        .heading {
          display: flex;
          align-items: center;
          --mdc-theme-primary: var(--primary-text-color);
        }

        .heading ha-textfield {
          flex-grow: 1;
        }

        ha-dialog {
          --dialog-z-index: 8;
          --dialog-content-padding: 0;
        }

        @media (min-width: 800px) {
          ha-dialog {
            --mdc-dialog-max-width: 800px;
            --mdc-dialog-min-width: 500px;
            --dialog-surface-position: fixed;
            --dialog-surface-top: 40px;
            --mdc-dialog-max-height: calc(100% - 72px);
          }
        }

        @media all and (max-width: 450px), all and (max-height: 500px) {
          ha-textfield {
            --mdc-shape-small: 0;
          }
        }

        @media all and (max-width: 450px), all and (max-height: 690px) {
          .hint {
            display: none;
          }
        }

        ha-icon.entity,
        ha-svg-icon.entity {
          margin-left: 20px;
        }

        ha-svg-icon.prefix {
          color: var(--primary-text-color);
        }

        ha-textfield ha-icon-button {
          --mdc-icon-button-size: 24px;
          color: var(--primary-text-color);
        }

        .command-category {
          --ha-chip-icon-color: #585858;
          --ha-chip-text-color: #212121;
        }

        .command-category.reload {
          --ha-chip-background-color: #cddc39;
        }

        .command-category.navigation {
          --ha-chip-background-color: var(--light-primary-color);
        }

        .command-category.server_control {
          --ha-chip-background-color: var(--warning-color);
        }

        span.command-text {
          margin-left: 8px;
        }

        mwc-list-item {
          width: 100%;
        }

        mwc-list-item.command-item {
          text-transform: capitalize;
        }

        .hint {
          padding: 20px;
          font-style: italic;
          text-align: center;
        }

        .nothing-found {
          padding: 16px 0px;
          text-align: center;
        }

        div[slot="trailingIcon"] {
          display: flex;
          align-items: center;
        }

        lit-virtualizer {
          contain: size layout !important;
        }
      `]}}]}}),i.oi)}}]);
//# sourceMappingURL=cf7c6579.js.map