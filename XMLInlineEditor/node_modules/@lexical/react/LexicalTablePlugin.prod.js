/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var c=require("@lexical/react/LexicalComposerContext"),r=require("@lexical/table"),t=require("@lexical/utils"),u=require("lexical"),v=require("react"),w;function y(l){let m=new URLSearchParams;m.append("code",l);for(let n=1;n<arguments.length;n++)m.append("v",arguments[n]);throw Error(`Minified Lexical error #${l}; visit https://lexical.dev/docs/error?${m} for the full message or `+"use the non-minified dev environment for full errors and additional helpful warnings.");}
w=y&&y.__esModule&&Object.prototype.hasOwnProperty.call(y,"default")?y["default"]:y;
exports.TablePlugin=function({hasCellMerge:l=!0,hasCellBackgroundColor:m=!0,hasTabHandler:n=!0}){let [e]=c.useLexicalComposerContext();v.useEffect(()=>{e.hasNodes([r.TableNode,r.TableCellNode,r.TableRowNode])||w(10);return t.mergeRegister(e.registerCommand(r.INSERT_TABLE_COMMAND,({columns:a,rows:d,includeHeaders:b})=>{a=r.$createTableNodeWithDimensions(Number(d),Number(a),b);t.$insertNodeToNearestRoot(a);a=a.getFirstDescendant();u.$isTextNode(a)&&a.select();return!0},u.COMMAND_PRIORITY_EDITOR),e.registerNodeTransform(r.TableNode,
a=>{[a]=r.$computeTableMapSkipCellCheck(a,null,null);let d=a.reduce((f,k)=>Math.max(f,k.length),0);for(let f=0;f<a.length;++f){var b=a[f].length;if(b===d)continue;let k=a[f][b-1].cell;for(;b<d;++b){let g=r.$createTableCellNode(0);g.append(u.$createParagraphNode());null!==k?k.insertAfter(g):t.$insertFirst(k,g)}}}))},[e]);v.useEffect(()=>{let a=new Map,d=e.registerMutationListener(r.TableNode,b=>{for(const [f,k]of b)"created"===k?e.getEditorState().read(()=>{var g=u.$getNodeByKey(f);if(r.$isTableNode(g)){const h=
g.getKey(),p=e.getElementByKey(h);p&&!a.has(h)&&(g=r.applyTableHandlers(g,p,e,n),a.set(h,g))}}):"destroyed"===k&&(b=a.get(f),void 0!==b&&(b.removeListeners(),a.delete(f)))},{skipInitialization:!1});return()=>{d();for(let [,b]of a)b.removeListeners()}},[e,n]);v.useEffect(()=>{if(!l)return e.registerNodeTransform(r.TableCellNode,a=>{if(1<a.getColSpan()||1<a.getRowSpan()){var [,,d]=r.$getNodeTriplet(a);[a]=r.$computeTableMap(d,a,a);let f=a.length,k=a[0].length;d=d.getFirstChild();r.$isTableRowNode(d)||
w(175);let g=[];for(let h=0;h<f;h++){0!==h&&(d=d.getNextSibling(),r.$isTableRowNode(d)||w(175));let p=null;for(let x=0;x<k;x++){var b=a[h][x];let q=b.cell;if(b.startRow===h&&b.startColumn===x)p=q,g.push(q);else if(1<q.getColSpan()||1<q.getRowSpan())r.$isTableCellNode(q)||w(176),b=r.$createTableCellNode(q.__headerState),null!==p?p.insertAfter(b):t.$insertFirst(d,b)}}for(let h of g)h.setColSpan(1),h.setRowSpan(1)}})},[e,l]);v.useEffect(()=>{if(!m)return e.registerNodeTransform(r.TableCellNode,a=>{null!==
a.getBackgroundColor()&&a.setBackgroundColor(null)})},[e,m,l]);return null}
