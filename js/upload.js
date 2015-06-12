(function(undefine){
    window.changefile = function(input){
        var file = input.files;
        if (file.length>0){
            var form = document.getElementById('upload');
            var show = document.getElementById('filename');
            show.innerHTML = '+- Change File'
            for (var i = 0; i<file.length; i++){
                var targetId = 'file_' + i;
                var targetSpanId = 'span_' + i;
                var now = document.getElementById(targetId);
                if (now!=undefine){
                    now.innerHTML = file[i].name;
                }else{
                    var tspan = document.createElement('span');
                    tspan.className = ' item file trans responsive';
                    tspan.id = targetSpanId;
                    var ta = document.createElement('a');
                    ta.href = 'javascript:void(0)';
                    ta.id = targetId;
                    ta.innerHTML = file[i].name;
                    tspan.appendChild(ta);
                    form.insertBefore(tspan, form.childNodes[0]);
                }
            }
            for (var i=file.length; true; i++){
                var targetSpanId = 'span_' + i;
                var now = document.getElementById(targetSpanId);
                if (now){
                    form.removeChild(now);
                }else
                    break;
            }
        }
    }
}());
