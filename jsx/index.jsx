require.config({
    baseUrl : '/js/',
    paths: {
        dom : "react/dom",
        react : "react",
        reactdom : "react-dom",
        ace : "AceEditor/ace",
        text : "text.min"
    },
    waitSeconds: 15,
    shim: {
        react : {
            exports: 'React'
        },
        reactdom : {
            deps: ['react'],
            exports: 'ReactDOM'
        },
        ace : {
            exports: 'ace'
        }
    },
    urlArgs: "v=" + (new Date()).getTime()
});

require(['react', 'reactdom', 'dom'], function(React, ReactDOM, dom, text){
    console.log(text);
    ReactDOM.render(
      <dom.Body json={d}/>,
      document.getElementById('react')
    );
})
