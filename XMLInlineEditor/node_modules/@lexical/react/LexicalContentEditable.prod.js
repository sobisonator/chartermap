/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var d=require("@lexical/react/LexicalComposerContext"),h=require("react"),m=require("react/jsx-runtime"),t=require("@lexical/text"),u=require("@lexical/utils");let v="undefined"!==typeof window&&"undefined"!==typeof window.document&&"undefined"!==typeof window.document.createElement?h.useLayoutEffect:h.useEffect;function w(...a){return c=>{a.forEach(b=>{"function"===typeof b?b(c):null!=b&&(b.current=c)})}}
let x=h.forwardRef(function({editor:a,ariaActiveDescendant:c,ariaAutoComplete:b,ariaControls:e,ariaDescribedBy:f,ariaExpanded:l,ariaLabel:y,ariaLabelledBy:z,ariaMultiline:A,ariaOwns:B,ariaRequired:C,autoCapitalize:D,className:E,id:F,role:n="textbox",spellCheck:G=!0,style:H,tabIndex:I,"data-testid":J,...K},p){let [g,q]=h.useState(a.isEditable()),r=h.useCallback(k=>{k&&k.ownerDocument&&k.ownerDocument.defaultView?a.setRootElement(k):a.setRootElement(null)},[a]),L=h.useMemo(()=>w(p,r),[r,p]);v(()=>{q(a.isEditable());
return a.registerEditableListener(k=>{q(k)})},[a]);return m.jsx("div",{...K,"aria-activedescendant":g?c:void 0,"aria-autocomplete":g?b:"none","aria-controls":g?e:void 0,"aria-describedby":f,"aria-expanded":g&&"combobox"===n?!!l:void 0,"aria-label":y,"aria-labelledby":z,"aria-multiline":A,"aria-owns":g?B:void 0,"aria-readonly":g?void 0:!0,"aria-required":C,autoCapitalize:D,className:E,contentEditable:g,"data-testid":J,id:F,ref:L,role:g?n:void 0,spellCheck:G,style:H,tabIndex:I})});
function M(a){return a.getEditorState().read(t.$canShowPlaceholderCurry(a.isComposing()))}function N(a){let [c,b]=h.useState(()=>M(a));v(()=>{function e(){let f=M(a);b(f)}e();return u.mergeRegister(a.registerUpdateListener(()=>{e()}),a.registerEditableListener(()=>{e()}))},[a]);return c}let P=h.forwardRef(O);
function O(a,c){let {placeholder:b,editor__DEPRECATED:e,...f}=a;a=e||d.useLexicalComposerContext()[0];return m.jsxs(m.Fragment,{children:[m.jsx(x,{editor:a,...f,ref:c}),null!=b&&m.jsx(Q,{editor:a,content:b})]})}
function Q({content:a,editor:c}){var b=N(c);let [e,f]=h.useState(c.isEditable());h.useLayoutEffect(()=>{f(c.isEditable());return c.registerEditableListener(l=>{f(l)})},[c]);if(!b)return null;b=null;"function"===typeof a?b=a(e):null!==a&&(b=a);return null===b?null:m.jsx("div",{"aria-hidden":!0,children:b})}exports.ContentEditable=P
