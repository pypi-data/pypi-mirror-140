var audioContext, audioSource, analyser, analyserRandom, canvas_ctx;
var requestIdAnimationFrame;
var spectrumAnalyserActive = false;
var spectrumAnalyserShow = false;

function setAudioContextVisual() {
    audio = document.getElementById("audio_with_controls");
    audioContext = new AudioContext();
    audioSource = audioContext.createMediaElementSource(audio);
    analyser = audioContext.createAnalyser();
    audioSource.connect(analyser).connect(audioContext.destination);
    // const prime_button = document.querySelectorAll('.btn-primary');
    // prime_button.forEach(btn => btn.removeEventListener('click',setAudioContextVisual, false));
}
;
function remove_page_cover() {
    setAudioContextVisual();
    document.getElementById("page_cover").style.display = "none";
};

$(document).ready(function () {
    // mouseover not accepted
    document.getElementById('page_cover').addEventListener('click', remove_page_cover);

    cookieStuff();
    // is_play_station();
    cookie_start_set_text_show_visuals();
    setInterval(delete_info, 2505);
    setInterval(meta_info, 5004);
    setInterval(toggle_show_select_box, 5003);
    setInterval(updateMasterprogress, 5002);
    setInterval(updateDisplay, 5001);

    const canvas = document.getElementById("canvas_master");
    const file_upload = document.getElementById("fileupload");
    const local_host_sound_route = "http://localhost:5050/sound/"
    const play_btn = document.getElementById("play_btn");
    const pause_btn = document.getElementById("pause_btn");
    const audio = document.getElementById("audio_with_controls");
    audio.volume = 0.25;
    const audio_volume_control = document.getElementById("audio_volume_controller");

    audio.addEventListener("play", function () {
        play_btn.style.display = "none";
        pause_btn.style.display = "block";
        pause_btn.style.cursor = "pointer";
        pause_btn.style.cursor = "hand";
        $("#pause_btn").on('click', function () {
            audio.pause();
        });
    });
    audio.addEventListener("pause", function () {
        play_btn.style.display = "block";
        pause_btn.style.display = "none";
        play_btn.style.cursor = "pointer";
        play_btn.style.cursor = "hand";
        $("#play_btn").on('click', function () {
            audio.play();
        });
    });

    audio_volume_control.addEventListener("input", setAudioVolume);

    file_upload.addEventListener("change", function () {
        var audio_duration;
        const playlist_title = document.getElementById("playlist_title");
        const playlist_section = document.getElementById("playlist_section");
        playlist_title.style.display = "block";
        playlist_section.style.display = "block";

        document.getElementById('lbl_div_audio').innerText = "local playlist"; /*current_station.substring(0, 20)*/
        document.getElementById('lbl_div_audio').style.cursor = "pointer";
        document.getElementById('lbl_div_audio').style.cursor = "hand";
        $("#lbl_div_audio").on('click', function () {
            document.getElementById('file_list').scrollIntoView({ behavior: "smooth" });
        });

        // console.log(this.files);
        const files = this.files;

        const clone_files = [...files];
        const audio = document.getElementById("audio_with_controls");
        const checkbox_shuffle = document.getElementById('checkbox_shuffle');
        var fileList = [];
        for (let i = 0; i < file_upload.files.length; i++) {
            fileList.push(file_upload.files[i]);
        }
        var play_list;
        play_list = fileList // for non shuffled
        if (checkbox_shuffle.checked) {
            // play_list = shuffle_array(fileList);    // destroys fileList org.
            play_list = shuffle_array(clone_files);
        }
        audio.src = URL.createObjectURL(play_list[0]);
        playlist_title.value = play_list[0].name;

        /*
    calculateMediaDuration(audio).then(() => {
        console.log(audio.duration);
    });
    */
        audio.load();
        audio.play;
        // setTimeout(() => {
        //     audio.pause();
        //     audio.currentTime = Number.MAX_SAFE_INTEGER; // chrome bug; NaN, infinity
        // }, audio_duration);
        if (!spectrumAnalyserActive) {
            visualiseAudio(null);
            spectrumAnalyserActive = true;
        }
        let track = 1;
        audio.onended = function () {
            if (track < play_list.length) {
                audio.src = "";   // remove from mem
                audio.currentTime = 0;
                audio.srcObject = null;
                audio.src = URL.createObjectURL(play_list[track]);
                playlist_title.value = play_list[track].name;
                audio.load();
                audio.play();

                track++;
            }
        }

    });  // file_up

    function is_play_station() {
        let req = $.ajax({
            type: 'GET',
            dataType: "json",
            url: "/is_play_station"
        });
        req.done(function (data) {

            let player_id = data.is_play_station_id;
            let player_name = data.is_play_station_name;
            if (player_id !== '-empty-') {
                audio.src = local_host_sound_route + player_name;
                audio.load();
                audio.play();
                if (!spectrumAnalyserActive) {
                    visualiseAudio(null);
                    spectrumAnalyserActive = true;
                }
            }
        });
    }
    ;

    function setAudioVolume() {
        audio.volume = audio_volume_control.value / 100;
    }
    ;

    $("button").click(function () {

        if ($(this).attr("class") === "navbar-toggle collapsed") {

            return;
        }
        ;

        let clicked = $(this).attr("name");
        console.log("send name " + clicked);
        let class_val = $(this).attr("class");
        console.log("send button " + class_val);
        let id = $(this).attr("id");
        let dict = {
            'name': clicked,
            'class_val': class_val,
            'button_id': id

        };
        req = $.ajax({
            type: 'POST',
            dataType: "json",
            url: "/",
            data: dict
        });
        $('#' + id).fadeOut(1).fadeIn(3);

        req.done(function (data) {

            if (data.class_val === "btn btn-primary") {
                $('#' + id).removeClass("btn btn-primary");
                $('#' + id).addClass("btn btn-danger");
            }
            ;

            if (data.class_val === "btn btn-danger") {
                $('#' + id).removeClass("btn btn-danger");
                $('#' + id).addClass("btn btn-primary");
            }
            ;

            if (data.streamer) {
                /* Del all streamer, push current in combo box */
                cookie_set_streamer();
                $('#cacheList').find('option:not(:first)').remove();
                let streamer = data.streamer.split(",");

                $.each(streamer, function (idx, val) {

                    let stream = val;
                    if (stream.length !== 0) {
                        stream = val.split("=");
                        let table_id = stream[1];
                        let title = stream[0];
                        cacheListFeed(table_id, title);

                        if (data.streamer === 'empty_json') {
                            $('#cacheList').find('option:not(:first)').remove();
                            document.getElementById('cacheList').style.color = "#696969";
                            document.getElementById('cacheList').style.textColor = "#696969";
                            cookie_del_streamer();
                        }
                        console.log('data.streamer ' + data.streamer);

                    }

                });    /*each*/

            }
            ;

            if (data.radio_table_id) {

            }
            ;

            /* current play station */

            if (data.table_ident) {

                var current_station = data.table_ident;
                console.log('table_ident ' + current_station);

                if (current_station !== 'Null') {

                    cookie_set_station(current_station, id);

                    document.getElementById('lbl_div_audio').innerText = current_station; /*current_station.substring(0, 20)*/
                    document.getElementById('lbl_div_audio').style.cursor = "pointer";
                    document.getElementById('lbl_div_audio').style.cursor = "hand";
                    $("#lbl_div_audio").on('click', function () {
                        document.getElementById('dot_' + id).scrollIntoView({ behavior: "smooth" });
                    });

                }
                if (data.former_button_to_switch) {
                    let num = data.former_button_to_switch;
                    console.log('auto_click former_button_to_switch: ' + num);
                    $("#" + num).click();
                }
                ;
            }
            ;

            if (data.result === 'deactivate_audio') {
                console.log('deactivate_audio');
                audio.src = "";
                audio.currentTime = 0;
                audio.srcObject = null;
                document.getElementById('lbl_div_audio').innerText = '';
                cookie_del_station();
            }
            ;

            if (data.result === 'activate_audio') {
                console.log('activate_audio');
                stopVisualiseAudio();

                try {
                    analyser = audioContext.createAnalyser();
                    audioSource.connect(analyser);
                    analyser.connect(audioContext.destination);
                } catch (error) {
                    console.error(error);
                };
                audio.volume = 0.25;
                audio_volume_control.value = 25;
                audio.src = "";
                audio.currentTime = 0;
                audio.srcObject = null;
                audio.src = local_host_sound_route + current_station;
                audio.load();
                audio.play();

                if (!spectrumAnalyserActive) {
                    analyserRandom = getRandomIntInclusive(1,2);
                    visualiseAudio(null);
                    spectrumAnalyserActive = true;
                }
            }
            ;

        });


    });

    function updateDisplay() {
        var req;

        req = $.ajax({
            type: 'GET',
            url: "/display_info",
            cache: false
        });

        req.done(function (data) {
            var displays = '';
            var display = '';
            var table_id = '';
            var title = '';

            displays = data.result.split(",");

            $.each(displays, function (idx, val) {
                display = val;

                if (display.length !== 0) {

                    display = val.split("=");
                    table_id = display[0];
                    title = display[1];
                    if (title !== 'Null') {
                        $('#Display_' + table_id).attr("value", title);
                    }
                    if (title === 'Null') {
                        $('#Display_' + table_id).attr("value", '');
                    }
                    // console.log(title)

                }

            });

        });


    }
    ;

    function updateMasterprogress() {
        var req;

        req = $.ajax({
            type: 'POST',
            url: "/index_posts_percent",
            cache: false,
            data: { 'percent': 'percent' }
        });

        req.done(function (data) {
            var percent = '';

            percent = data.result;
            // console.log('########### '+percent+' #########');
            if (percent === 0) {
                $('.progress-bar').css('width', 25 + '%').attr('aria-valuenow', 25).html('Timer Off');
            }
            if (percent !== 0) {
                $('.progress-bar').css('width', percent + '%').attr('aria-valuenow', percent).html('Run, Forrest! RUN!');
                if (percent >= 100) {
                    window.location.href = "/page_flash";
                }
            }

        });


    }
    ;

    function visualiseAudio(var_canvas) {

        // const canvas = document.getElementById("canvas_" + var_canvas);
        // console.log('show canvas: ' + var_canvas)
        canvas_ctx = canvas.getContext('2d');
        requestIdAnimationFrame = undefined;

        let barHeight;
        let x = 0;

        try {
            if (analyserRandom === 1) { rotateVisualiser();}
            if (analyserRandom === 2) { draw();}
            // if (analyserRandom === 3) { animate();}
        } catch (error) {console.error(error);}

    }
    ;

    function stopVisualiseAudio() {
       window.cancelAnimationFrame(requestIdAnimationFrame);
       requestIdAnimationFrame = undefined;
       spectrumAnalyserActive = false;
    }
    ;

    // animate();
    function animate() {
        if (!spectrumAnalyserShow) {
            spectrumAnalyserActive = false;
            return;
        }
        x = 0;
        analyser.fftSize = 128;
        const bufferLength = analyser.frequencyBinCount;
        var barWidth = (canvas.width / bufferLength) * 2; // const barWidth = (canvas.width/2) / bufferLength;
        const dataArray = new Uint8Array(bufferLength);

        analyser.getByteFrequencyData(dataArray);
        canvas_ctx.clearRect(0, 0, canvas.width, canvas.height);
        requestIdAnimationFrame = requestAnimationFrame(animate);

        for (let i = 0; i < bufferLength; i++){
            barHeight = (dataArray[i] / 2) + 2;
            let darkBody = getBodyColor(); 
            if (darkBody) {
                canvas_ctx.fillStyle = 'red';  //  #d441fc
                canvas_ctx.fillRect(x, canvas.height - barHeight - 3, barWidth, 18);
                canvas_ctx.fillStyle = 'rgb(219, 111, 52)';  //  #d441fc
                canvas_ctx.fillRect(x, canvas.height - barHeight - 6, barWidth, 2);
                canvas_ctx.fillStyle = 'blue';
                canvas_ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            } else {
                canvas_ctx.fillStyle = '#bc5090';  //  #d441fc
                canvas_ctx.fillRect(x, canvas.height - barHeight - 3, barWidth, 18);
                canvas_ctx.fillStyle = 'black';  //  #d441fc
                canvas_ctx.fillRect(x, canvas.height - barHeight - 6, barWidth, 2);
                canvas_ctx.fillStyle = '#565454';
                canvas_ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            }

            x += barWidth;

        }
    };

    // draw();
    function draw() {
        if (!spectrumAnalyserShow) {
            spectrumAnalyserActive = false;
            return;
        }
        requestIdAnimationFrame = requestAnimationFrame(draw);
        analyser.fftSize = 2048;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteTimeDomainData(dataArray);

        canvas_ctx.clearRect(0, 0, canvas.width, canvas.height);
        let darkBody = getBodyColor();
        if (darkBody) {
            canvas_ctx.lineWidth = 1.5;
            canvas_ctx.strokeStyle = 'rgb(219, 111, 52)';
        } else {
            canvas_ctx.lineWidth = 1.0;
            canvas_ctx.strokeStyle = 'red';
        }
        canvas_ctx.beginPath();
        var sliceWidth = canvas.width * 1.0 / bufferLength;
        var x = 0;

        for (var i = 0; i < bufferLength; i++) {
            var v = dataArray[i] / 128.0;
            var y = v * canvas.height / 2;

            if (i === 0) {
                canvas_ctx.moveTo(x, y);
            } else {
                canvas_ctx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvas_ctx.lineTo(canvas.width, canvas.height / 2);
        canvas_ctx.stroke();
    };

    // rotateVisualiser();
    function rotateVisualiser() {
        if (!spectrumAnalyserShow) {
            spectrumAnalyserActive = false;
            return;
        }
        let div_canvas = document.getElementById('div_canvas_master');
        analyser.fftSize = 128;
        const bufferLength = analyser.frequencyBinCount;
        var barWidth = (canvas.width / bufferLength) * 2; // const barWidth = (canvas.width/2) / bufferLength;
        const dataArray = new Uint8Array(bufferLength);
        barWidth = (canvas.width/2) / bufferLength;
        requestIdAnimationFrame = requestAnimationFrame(rotateVisualiser);

        x = 0;
        analyser.getByteFrequencyData(dataArray);
        canvas_ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < bufferLength; i++){
            barHeight = dataArray[i] * 0.36;
            canvas_ctx.save();
            let darkBody = getBodyColor();
            // if (!darkBody) {
            //     canvas.style.background = "black";
            // } else {
            //     canvas.style.background = "rgba(26,26,26,1)";
            // }
            canvas_ctx.translate(canvas.width/2, canvas.height/2);
            canvas_ctx.rotate(i * Math.PI * 4 / bufferLength);
            const hue = i * 5;
            canvas_ctx.fillStyle = 'hsl(' + hue + ',100%,50%)';
            canvas_ctx.fillRect(0, 0, barWidth, barHeight);
            x += barWidth;
            canvas_ctx.restore();
        }
    };
    
    
}); /* doc.window */


function setDarkmode() {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/setcookiedark",
        cache: false
    });

}
;

function delDarkmode() {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/delcookiedark",
        cache: false
    });

}
;

function getDarkmode() {
    let req;

    req = $.ajax({
        type: 'GET',
        url: "/getcookiedark",
        cache: false
    });

    req.done(function (data) {
        let dark = '';

        dark = data.darkmode;
        if (dark === 'darkmode') {
            setColor('cookie_request_on_load_is_dark');
        }


    });

}
;

function cookie_set_station(station, station_id) {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/cookie_set_station",
        cache: false,
        dataType: "json",
        data: { 'station': station, 'station_id': station_id }
    });
}
;

function cookie_get_station() {
    let req;

    req = $.ajax({
        type: 'GET',
        url: "/cookie_get_station",
        cache: false
    });

    req.done(function (data) {
        let play_station = '';
        if (data.play_station !== null) {
            if (data.play_station !== ',') {
                play_station = data.play_station.split(",");
                let station = play_station[0];
                let station_id = play_station[1];

                document.getElementById('lbl_div_audio').innerText = station; /*station.substring(0, 20)*/
                document.getElementById('lbl_div_audio').setAttribute("id", "lbl_div_audio");

                document.getElementById('lbl_div_audio').style.cursor = "pointer";
                document.getElementById('lbl_div_audio').style.cursor = "hand";
                $("#lbl_div_audio").on('click', function () {
                    document.getElementById('dot_' + station_id).scrollIntoView({ behavior: "smooth" });
                });
            }/* if */
        }

    });

}
;

function cookie_del_station() {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/cookie_del_station",
        cache: false
    });

}
;

function cookie_set_streamer() {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/cookie_set_streamer",
        cache: false
    });
}
;

function cookie_del_streamer() {
    let req;
    req = $.ajax({
        type: 'POST',
        url: "/cookie_del_streamer",
        cache: false
    });
}
;

function cookie_get_streamer() {
    let req;

    req = $.ajax({
        type: 'GET',
        url: "/cookie_get_streamer",
        cache: false,
    });

    req.done(function (data) {

        if (data.str_streamer) {
            $('#cacheList').find('option:not(:first)').remove();

            let streamer = data.str_streamer.split(",");

            $.each(streamer, function (idx, val) {
                let stream = val;

                if (stream.length !== 0) {
                    if (data.str_streamer === 'empty_json') {

                        $('#cacheList').find('option:not(:first)').remove();
                        cookie_del_streamer();
                        return;
                    }
                    stream = val.split("=");
                    let table_id = stream[1];
                    let title = stream[0];
                    cacheListFeed(table_id, title);
                }

            });

        }
        ; /*if (data.streamer)*/

    });  /*req.done*/

}
;  /*function cookie_get_streamer*/

function cookie_set_show_visuals() {
    let req;

    req = $.ajax({
        type: 'POST',
        url: "/cookie_set_show_visuals",
        cache: false
    });
}
;

function cookie_del_show_visuals() {
    let req;
    req = $.ajax({
        type: 'POST',
        url: "/cookie_del_show_visuals",
        cache: false
    });
}
;

function cookie_toggle_show_visuals() {
    let req;

    req = $.ajax({
        type: 'GET',
        url: "/cookie_get_show_visuals",
        cache: false
    });

    req.done(function (data) {
        let analyzer_badge = document.getElementById('analyzer_badge');
        let canvas = document.getElementById('canvas_master');
        let div_canvas = document.getElementById('div_canvas_master');
        let show_visuals = data.str_visuals;
        if (show_visuals !== 'show_visuals') {            analyzer_badge.textContent = "hide";
            canvas.style.display = "inline-block";
            div_canvas.style.display = "inline-block";
            cookie_set_show_visuals();

            var ctx = canvas.getContext("2d");
            ctx.font = "16px Arial";
            ctx.fillStyle = "rgb(219, 111, 52)";
            ctx.fillText("reload page to activate analyser",10,50);


        }
        if (show_visuals === 'show_visuals') {
            analyzer_badge.textContent = "show";
            canvas.style.display = "none";
            div_canvas.style.display = "none";
            cookie_del_show_visuals();

        }


    });

}
;
function cookie_start_set_text_show_visuals() {
    let req;

    req = $.ajax({
        type: 'GET',
        url: "/cookie_get_show_visuals",
        cache: false
    });

    req.done(function (data) {
        let analyzer_badge = document.getElementById('analyzer_badge');
        let div_canvas = document.getElementById('div_canvas_master');
        let canvas = document.getElementById('canvas_master');
        let show_visuals = data.str_visuals;
        if (show_visuals === 'show_visuals') {
            analyzer_badge.textContent = "hide";
            canvas.style.display = "inline-block";
            div_canvas.style.display = "inline-block";
            spectrumAnalyserShow = true;
            if (!spectrumAnalyserActive) {
                var ctx = canvas.getContext("2d");
                ctx.font = "16px Arial";
                ctx.fillStyle = "rgb(219, 111, 52)";
                ctx.fillText("change radio to activate analyser",10,50);

            }

        }
        if (show_visuals !== 'show_visuals') {
            analyzer_badge.textContent = "show";
            canvas.style.display = "none";
            div_canvas.style.display = "none";
            spectrumAnalyserShow = false;
        }


    });

}
;




function setTimer(val) {

    $.ajax({
        type: 'POST',
        url: "/index_posts_combo",
        cache: false,
        data: { 'time_record_select_all': val }

    });
}
;

function setColor(val) {
    let req;
    var color;
    if (val === 'cookie_request_on_load_is_dark') {
        color = 'black'
    }
    if (val === 'view') {
        color = 'white'
    }

    req = $.ajax({
        type: 'GET',
        url: "/getcookiedark",
        cache: false
    });
    req.done(function (data) {
        let dark = '';

        dark = data.darkmode;
        if (dark !== 'darkmode') {
            color = 'black';
        }

        var bodyStyles = document.body.style;
        if (color === 'black') {
            bodyStyles.setProperty('--background-color', 'rgba(26,26,26,1)');
            bodyStyles.setProperty('--form-background', '#333333');
            bodyStyles.setProperty('--form-text', '#f1f1f1');
            bodyStyles.setProperty('--hr-color', '#777777');
            bodyStyles.setProperty('--border-color', '#202020');
            bodyStyles.setProperty('--text-color', '#bbbbbb');
            bodyStyles.setProperty('--form-edit', '#333333');
            bodyStyles.setProperty('--opacity', '0.5');
            bodyStyles.setProperty('--btn-opacity', '0.75');
            bodyStyles.setProperty('--footer-color', 'rgba(26,26,26,0.90)');
            bodyStyles.setProperty('--main-display-arrow', '#34A0DB');
            bodyStyles.setProperty('--dot-for-radio-headline', '#E74C3C');
            bodyStyles.setProperty('--lbl-div-audio', '#db6f34');
            bodyStyles.setProperty('--ghetto-measurements-bottom-color', '#FCA841');
            bodyStyles.setProperty('--radio-station-headline', '#4195fc');
            bodyStyles.setProperty('--controls-background', 'rgba(26,26,26,1)');
            bodyStyles.setProperty('--canvas_master', 'rgba(26,26,26,0.85)');

            setDarkmode();
        }
        if (color === 'white') {
            bodyStyles.setProperty('--background-color', '#ccc');
            bodyStyles.setProperty('--form-background', '#ddd');
            bodyStyles.setProperty('--form-text', '#565454');
            bodyStyles.setProperty('--hr-color', '#eee');
            bodyStyles.setProperty('--border-color', '#eee');
            bodyStyles.setProperty('--text-color', '#f0f0f0');
            bodyStyles.setProperty('--form-edit', '#777777');
            bodyStyles.setProperty('--opacity', '1');
            bodyStyles.setProperty('--btn-opacity', '1');
            bodyStyles.setProperty('--footer-color', 'rgba(0,63,92,0.90)');
            bodyStyles.setProperty('--main-display-arrow', '#bc5090');
            bodyStyles.setProperty('--dot-for-radio-headline', '#565454');
            bodyStyles.setProperty('--lbl-div-audio', '#FCA841');
            bodyStyles.setProperty('--ghetto-measurements-bottom-color', '#d441fc');
            bodyStyles.setProperty('--radio-station-headline', '#565454');
            bodyStyles.setProperty('--controls-background', '#565454');
            bodyStyles.setProperty('--canvas_master', '#ccc');    // rgba(240, 240, 240, 0.85)

            delDarkmode();
        }
    });
}
;


function cookieStuff() {
    getDarkmode();

    cookie_set_streamer();
    cookie_get_streamer();
    cookie_set_station();
    cookie_get_station();
}
;

function meta_info() {

    let req = $.ajax({
        type: 'GET',
        url: "/cache_info",
        cache: false
    });

    req.done(function (data) {
        if (data.cache_result !== "-empty-") {
            let dict_io_lists = data.cache_result
            $.each(dict_io_lists, function (idx, val) {

                let response_time = val[0];
                let suffix = val[1];
                let genre = val[2];
                let station_name = val[3];
                let station_id = val[4];
                let bit_rate = val[5];
                let icy_url = val[6];

                document.getElementById('request_time_' + station_id).innerText = "" + response_time + " ms";
                document.getElementById('request_suffix_' + station_id).innerText = "" + suffix;
                document.getElementById('request_icy_br_' + station_id).innerText = "" + bit_rate + " kB/s";
                document.getElementById('icy_name_' + station_id).innerText = "" + station_name;
                document.getElementById('request_icy_genre_' + station_id).innerText = "" + genre;
                document.getElementById('request_icy_url_' + station_id).innerText = "" + icy_url;
                document.getElementById('request_icy_url_' + station_id).value = "" + icy_url;
            });
        }   /*data.cache_result !== ""*/
    });
}
;

function delete_info() {

    let req = $.ajax({
        type: 'GET',
        url: "/delete_info",
        cache: false
    });

    req.done(function (data) {

        if (data.stopped_result !== "-empty-") {
            let stopped_list = data.stopped_result;

            $.each(stopped_list, function (idx, val) {

                let station_id = val;
                document.getElementById('request_time_' + station_id).innerText = "";
                document.getElementById('request_suffix_' + station_id).innerText = "";
                document.getElementById('request_icy_br_' + station_id).innerText = "";
                document.getElementById('request_icy_url_' + station_id).innerText = "";
                document.getElementById('icy_name_' + station_id).innerText = "";
                document.getElementById('request_icy_genre_' + station_id).innerText = "";
                document.getElementById("canvas_" + station_id).style.display = "none";
            });/**/
        }
    });
}
;

function cacheListFeed(table_id, title) {

    if (title !== 'Null') {

        let cacheList = document.getElementById('cacheList');
        cacheList.style.color = "#db6f34";
        cacheList.style.textColor = "#db6f34";

        let opt = document.createElement('option');
        opt.id = 'opt_' + table_id;
        opt.value = '#dot_' + table_id;
        opt.innerHTML = title;
        cacheList.appendChild(opt);
    }
}
;

function toggle_show_select_box() {
    if (document.getElementById('cacheList').style.color !== "rgb(219, 111, 52)") {
        document.getElementById("cacheList").style.display = "none";
    }
    if (document.getElementById('cacheList').style.color === "rgb(219, 111, 52)") {
        document.getElementById("cacheList").style.display = "block";
    }
}
;

// Convert base64 string to ArrayBuffer
function _base64ToArrayBuffer(base64) {
    var binary_string = window.atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}
;

update_file_list = function () {
    var input = document.getElementById('fileupload');
    var output = document.getElementById('file_list');
    var children = "";
    for (let i = 0; i < input.files.length; ++i) {
        children.id = "playlist_num_" + i;
        children += '<li>' + input.files.item(i).name + '</li>';
    }
    output.innerHTML = '<ul>' + children + '</ul>';
}
    ;

/**
 * Shuffles array in place. ES6 version
 * @param {Array} a items An array containing the items.
 * https://stackoverflow.com/questions/6274339/how-can-i-shuffle-an-array
 */
function shuffle_array(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}
;

/**
 *  calculateMediaDuration()
 *  Force media element duration calculation.
 *  Returns a promise, that resolves when duration is calculated
 **/
function calculateMediaDuration(media) {
    return new Promise((resolve, reject) => {
        media.onloadedmetadata = function () {
            // set the mediaElement.currentTime  to a high value beyond its real duration
            media.currentTime = Number.MAX_SAFE_INTEGER;
            // listen to time position change
            media.ontimeupdate = function () {
                media.ontimeupdate = function () { };
                // setting player currentTime back to 0 can be buggy too, set it first to .1 sec
                media.currentTime = 0.1;
                media.currentTime = 0;
                // media.duration should now have its correct value, return it...
                resolve(media.duration);
            }
        }
    });
}
;

function getBodyColor() {
    let bodyStyle = window.getComputedStyle(document.body, null);
    let backgroundColor = bodyStyle.backgroundColor;
    if (backgroundColor === 'rgb(26, 26, 26)') {
        var darkBody = true;
    } else { darkBody = false; }
    return darkBody;
}
;

function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min +1)) + min;
}
;



