const change_btn = document.getElementById("change_button");
const play_btn = document.getElementById("play")
const ep_selector = document.getElementById("episode_selector");
const player = document.getElementById('audio_player')
const mp3_prefix = "data:audio/mp3;base64, "
let audio_buffer = ""

function delay(milliseconds){
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

load_audio = async (episode_id) => {
    let n_chunks = 2 // Eventually replace with some lookup logic from database
    let full_audio = ""
    console.log(`Loading episode id ${episode_id}`)
    for (i=0; i < n_chunks; i++){
        console.log(`starting loop ${i}`)
        // const res = await fetch(`/audio_by_id/${episode_id}`);
        // let {snd: b64buf} = await res.json();
        // full_audio = append_audio_buf(b64buf)
        // await delay(50)
        fetch_uri = `/audio_by_id/${episode_id}`
        console.log(`fetching from ${fetch_uri}`)
        fetch(`/audio_by_id/${episode_id}`).then(
            (res) => {
                res.json().then(
                    (res) => {
                        let {snd: b64buf} = res
                        console.log(`chunk length is ${b64buf.length}`)
                        if (i==0) {
                            player.src = `${mp3_prefix}${b64buf}`
                            full_audio = full_audio + b64buf
                        } else {
                            // let curr_buf = player.src.substring(mp3_prefix.length)
                            // let new_buf = curr_buf + b64buf
                            // player.src = mp3_prefix+new_buf;
                            let curr_time = player.currentTime
                            player.src = player.src + b64buf
                            player.currentTime = curr_time
                            full_audio = full_audio + b64buf
                        }
                        console.log(`after i=${i} player src length is ${player.src.length}`)
                    }
                )
            }
        )
        await delay(2000)
    }
    console.log(`Loaded episode id ${episode_id}`)
    play_btn.value = 'Play/Pause'
    return full_audio
}

append_audio_buf = (buf) => {
    let curr_buf = player.src.substring(mp3_prefix.length)
    let new_buf = curr_buf + buf
    let curr_time = player.currentTime
    player.src = mp3_prefix+new_buf;
    player.currentTime = curr_time
    return new_buf
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

change_player_time = (delta_seconds) => {
    player.currentTime += delta_seconds
}

update_audio = (episode_id) => {
    console.log('entering update_audio')
    play_btn.innerHTML = 'Loading...'
    load_audio(episode_id).then(
        (full_audio) => {
            // let audio_buffer = res
            let save_time = check_player_time()
            player.src = `${mp3_prefix}${full_audio}`
            play_btn.innerHTML = 'Play/Pause'
            player.currentTime = save_time
        }
    )    
}

change_btn.addEventListener("click", function () {
    console.log('received click for audio buffer')
    update_audio(ep_selector.value)
});

play_btn.addEventListener("click", function () {
    console.log(`Playing audio src ${mp3_prefix}${audio_buffer}`)
    let player = new Audio(`${mp3_prefix}${audio_buffer}`)
})

