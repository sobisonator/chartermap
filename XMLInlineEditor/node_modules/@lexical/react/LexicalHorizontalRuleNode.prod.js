/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var b=require("@lexical/react/LexicalComposerContext"),f=require("@lexical/react/useLexicalNodeSelection"),g=require("@lexical/utils"),h=require("lexical"),l=require("react"),p=require("react/jsx-runtime");let q=h.createCommand("INSERT_HORIZONTAL_RULE_COMMAND");
function r({nodeKey:a}){let [d]=b.useLexicalComposerContext(),[e,m,n]=f.useLexicalNodeSelection(a),k=l.useCallback(c=>e&&h.$isNodeSelection(h.$getSelection())&&(c.preventDefault(),c=h.$getNodeByKey(a),t(c))?(c.remove(),!0):!1,[e,a]);l.useEffect(()=>g.mergeRegister(d.registerCommand(h.CLICK_COMMAND,c=>{let w=d.getElementByKey(a);return c.target===w?(c.shiftKey||n(),m(!e),!0):!1},h.COMMAND_PRIORITY_LOW),d.registerCommand(h.KEY_DELETE_COMMAND,k,h.COMMAND_PRIORITY_LOW),d.registerCommand(h.KEY_BACKSPACE_COMMAND,
k,h.COMMAND_PRIORITY_LOW)),[n,d,e,a,k,m]);l.useEffect(()=>{let c=d.getElementByKey(a);null!==c&&(e?g.addClassNamesToElement(c,"selected"):g.removeClassNamesFromElement(c,"selected"))},[d,e,a]);return null}
class u extends h.DecoratorNode{static getType(){return"horizontalrule"}static clone(a){return new u(a.__key)}static importJSON(){return v()}static importDOM(){return{hr:()=>({conversion:x,priority:0})}}exportJSON(){return{type:"horizontalrule",version:1}}exportDOM(){return{element:document.createElement("hr")}}createDOM(a){let d=document.createElement("hr");g.addClassNamesToElement(d,a.theme.hr);return d}getTextContent(){return"\n"}isInline(){return!1}updateDOM(){return!1}decorate(){return p.jsx(r,
{nodeKey:this.__key})}}function x(){return{node:v()}}function v(){return h.$applyNodeReplacement(new u)}function t(a){return a instanceof u}exports.$createHorizontalRuleNode=v;exports.$isHorizontalRuleNode=t;exports.HorizontalRuleNode=u;exports.INSERT_HORIZONTAL_RULE_COMMAND=q
