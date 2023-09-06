const btn = document.getElementById("change_button");
const ep_selector = document.getElementById("episode_selector");
const player = document.getElementById('audio_player')
const mp3_prefix = "data:audio/mp3;base64, "

function delay(milliseconds){
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

update_audio = async (episode_id) => {
    player.src = mp3_prefix
    
    let n_chunks = 1 // Eventually replace with some lookup logic from database
    for (i=0; i < n_chunks; i++){
        const res = await fetch(`/audio_by_id/${episode_id}`);
        let {snd: b64buf} = await res.json();
        let is_paused = player.paused
        console.log(`player is paused? ${is_paused}`)
        append_audio_buf(b64buf)
        player.paused = is_paused
        console.log(`Updated and player is now: ${player.paused}`)
        await delay(5000)
    }
}

append_audio_buf = (buf) => {
    let curr_buf = player.src.substring(mp3_prefix.length)
    let new_buf = curr_buf + buf
    let curr_time = player.currentTime
    player.src = mp3_prefix+new_buf;
    player.currentTime = curr_time
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

change_player_time = (delta_seconds) => {
    player.currentTime += delta_seconds
}

btn.addEventListener("click", function () {
    update_audio(ep_selector.value)
});

