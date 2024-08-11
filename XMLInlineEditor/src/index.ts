import {registerDragonSupport} from '@lexical/dragon';
import {createEmptyHistoryState, registerHistory} from 'lexical/history'; 
import {HeadingNode, QuoteNode, registerRichText} from 'lexical/rich-text';
import {mergeRegister} from 'lexical/utils';
import {createEditor} from 'lexical';

document.querySelector<HTMLDivElement>('#app')!.innerHTML =
    