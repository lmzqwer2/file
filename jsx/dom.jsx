define(function(require){
    var React = require('react');
    var TitleChain = React.createClass({
        render : function(){
            var createChainItem = function(item){
                return (
                    <span className='folder' key={item.url}>
                        <a href={item.url}>{item.name}</a>
                    </span>
                );
            }
            var list = ['div', { className: 'path' }];
            var downloadurl = "/download" + this.props.url;
            list = list.concat(this.props.chain.map(createChainItem));
            if (this.props.isfile){
                list.push(
                    <div className='download'>
                        <a href={downloadurl} className='trans link-skewed'>Download</a>
                    </div>
                );
            }
            return React.createElement.apply(window, list);
        }
    })
    var Title = React.createClass({
        render: function(){
            var createInfoItem = function(item, index){
                return (
                    <p key={index}>{item}</p>
                );
            }
            var list = [ 'div', { id: 'title', className: 'title' }];
            list.push(
                <TitleChain chain={this.props.chain} isfile={this.props.isfile} url={this.props.url}/>
            );
            if (this.props.info !== undefined){
                list.push(<div className='info'>{this.props.info.map(createInfoItem)}</div>);
            }
            return React.createElement.apply(window, list);
        }
    });
    var Folder = React.createClass({
        render: function(){
            var createItem = function(item){
                className = item.filetype + ' ' + "item trans responsive";
                title = item.filetype + ':' + item.name;
                return (
                    <li className={className} key={item.link}>
                        <acronym title={title}>
                            <a href={item.link}>{item.name}</a>
                        </acronym>
                    </li>
                );
            }
            return (
                <ul className='container'>{this.props.list.map(createItem)}</ul>
            );
        }
    });
    var Uploader = React.createClass({
        getInitialState : function(){
            return {
                file : [],
                hasFile : false
            };
        },
        fileChange : function(event){
            var files = this.refs.file.files;
            list = []
            for (var i=0; i<files.length; i++){
                list.push({
                    name: files[i].name
                });
            }
            this.setState({
                file : list,
                hasFile : files.length > 0
            })
        },
        render: function(){
            var createItem = function(item){
                return (
                    <span className='item file trans responsive' key={item.name}>
                        <a href='javascript:void(0)'>{item.name}</a>
                    </span>
                )
            }
            return (
                <div className='container'>
                    <form action='.' encType="multipart/form-data" method='post' className='item dir trans upload'>
                        {this.state.file.map(createItem)}
                        <span className='uploadbutton item trans responsive'>
                            <input ref='file' type='file' className='uploadfile' name='file' multiple onChange={this.fileChange}/>
                            <a href='javascript:void(0)' className='uploadtext'>
                                {this.state.hasFile ? '+- Change File' : '+ Add file'}
                            </a>
                        </span>
                        <span className='uploadbutton item trans responsive'>
                            <input type='submit' className='uploadsubmit' name='submit' value='Upload'/>
                            <a href='javascript:void(0)' className='uploadtext'>Upload</a>
                        </span>
                    </form>
                </div>
            );
        }
    });
    var Editor = React.createClass({
        getDefaultProps : function(){
            return {
                fontsizeArray : [
                    { 'width': 400, 'font' : '1.1em' },
                    { 'width': 750, 'font' : '1.2em' },
                    { 'width': 1050, 'font' : '1.3em' },
                    { 'width': 1400, 'font' : '1.4em' },
                    { 'width': 1750, 'font' : '1.5em' }
                ]
            }
        },
        componentDidMount : function(){
            var self = this;
            if (this.props.type.readable){
                require(["ace", "text!/text" + this.props.url], function(ace, text){
                    var fontsizeArray = self.props.fontsizeArray;
                    var editor = ace.edit("AceEditor");
                    editor.setTheme("ace/theme/iplastic");
                    editor.setValue(text);
                    editor.gotoLine(0);
                    if (self.props.type.js)
                        editor.session.setMode("ace/mode/" + self.props.type.js);
                    var AceEditor = document.getElementById("AceEditor");
                    var title = document.getElementById('title');
                    AceEditor.style.fontSize = '1.1em';
                    (function(){
                        function resizeAceEditor(e){
                            var inheight = window.innerHeight
                                || document.documentElement.clientHeight
                                || document.body.clientHeight
                                +1;
                            var inWidth = window.innerWidth
                                || document.documentElement.clientWidth
                                || document.body.clientWidth
                                +1;
                            var titleHeight = (title.innerHeight || title.clientHeight || title.offsetHeight) || 0;
                            AceEditor.style.height = (inheight - titleHeight) + 'px';
                            var index = 0;
                            while (index + 1 < fontsizeArray.length && fontsizeArray[index].width < inWidth) index++;
                            AceEditor.style.fontSize = fontsizeArray[index].font;
                            editor.resize();
                        };
                        resizeAceEditor();
                        window.addEventListener('resize', resizeAceEditor);
                        setInterval(function(){
                            resizeAceEditor();
                        }, 200);
                    })();
                    self.forceUpdate();
                });
            }
        },
        render : function(){
            var className = "AceEditor " + this.props.type.ext;
            var text = this.props.type.readable ? this.props.text : "Not a text file."
            return (
                <div><pre id="AceEditor" className={className}>{text}</pre></div>
            );
        }
    });
    var Body = React.createClass({
        render: function(){
            console.log(this.props.json);
            var list = ['div', null];
            var chain = this.props.json.chain;
            var url = chain[chain.length-1].url;
            list.push(<Title chain={this.props.json.chain} info={this.props.json.info} url={url} isfile={this.props.json.isfile}/>);
            if (this.props.json.isfile){
                list.push(<Editor type={this.props.json.type} text='Loading...' url={url}/>);
            }else{
                if (this.props.json.upload){
                    list.push(
                        <Uploader/>
                    );
                }
                list.push(<Folder list={this.props.json.list}/>);
            }
            return (
                React.createElement.apply(window, list)
            );
        }
    });
    return {
        Body : Body
    }
});
