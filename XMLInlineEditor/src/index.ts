import {registerDragonSupport} from '@lexical/dragon';
import {createEmptyHistoryState, registerHistory} from '@lexical/history'; 
import {HeadingNode, QuoteNode, registerRichText} from '@lexical/rich-text';
import {mergeRegister} from '@lexical/utils';
import {createEditor} from 'lexical';

document.querySelector<HTMLDivElement>('#app')!.innerHTML = /*html*/`
    <div>
        <h1>Lexical Basic - Vanilla JS</h1>
        <div class="editor-wrapper">
            <div id="lexical-editor" contenteditable></div>
        </div>
        <h4>Editor state:</h4>
        <textarea id="lexical-state"></textarea>
    </div>
`;

const editorRef = document.getElementById('lexical-editor');
const stateRef = document.getElementById(
    'lexical-state',
) as HTMLTextAreaElement;

const initialConfig = {
    namespace: 'Lexical vanilla JS demo',
    // Register nodes specific for @lexical/rich-text
    nodes: [HeadingNode, QuoteNode],
    onError: (error: Error) => {
        throw error;
    },
    theme: {
        // No styling available
        // quote: 'PlaygroundEditorTheme__quote',
    },
};

const editor = createEditor(initialConfig);
editor.setRootElement(editorRef);

// Registering plugins
mergeRegister(
    registerRichText(editor),
    registerDragonSupport(editor),
    registerHistory(editor, createEmptyHistoryState(), 300),
);

editor.registerUpdateListener(({editorState}) => {
    stateRef!.value = JSON.stringify(editorState.toJSON(), undefined, 2);
})