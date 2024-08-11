/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var e=require("@lexical/react/LexicalComposerContext"),f=require("lexical"),g=require("react"),m=require("react/jsx-runtime");let n="undefined"!==typeof window&&"undefined"!==typeof window.document&&"undefined"!==typeof window.document.createElement,p=n?g.useLayoutEffect:g.useEffect,q={tag:"history-merge"};
function r(a,c){if(null!==c)if(void 0===c)a.update(()=>{var b=f.$getRoot();if(b.isEmpty()){let d=f.$createParagraphNode();b.append(d);b=n?document.activeElement:null;(null!==f.$getSelection()||null!==b&&b===a.getRootElement())&&d.select()}},q);else if(null!==c)switch(typeof c){case "string":let b=a.parseEditorState(c);a.setEditorState(b,q);break;case "object":a.setEditorState(c,q);break;case "function":a.update(()=>{f.$getRoot().isEmpty()&&c(a)},q)}}
exports.LexicalComposer=function({initialConfig:a,children:c}){let b=g.useMemo(()=>{const {theme:d,namespace:h,editor__DEPRECATED:t,nodes:u,onError:v,editorState:w,html:x}=a,y=e.createLexicalComposerContext(null,d);let k=t||null;if(null===k){const l=f.createEditor({editable:a.editable,html:x,namespace:h,nodes:u,onError:z=>v(z,l),theme:d});r(l,w);k=l}return[k,y]},[]);p(()=>{let d=a.editable,[h]=b;h.setEditable(void 0!==d?d:!0)},[]);return m.jsx(e.LexicalComposerContext.Provider,{value:b,children:c})}
