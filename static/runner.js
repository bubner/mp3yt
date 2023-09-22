/**
 * Dynamic runner for mp3yt
 * @author Lucas Bubner, 2023
 */

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("mp3").addEventListener("click", (e) => queue(e));
    document.getElementById("mp4").addEventListener("click", (e) => queue(e));
});

function queue(e) {
    const type = e.target.id;
    const url = document.getElementById("link").value;
    if (!url) return;

    document.getElementById("link").value = "Processing...";
    document.getElementById("link").disabled = true;

    let vidTitle = "download";
    fetch("/title?url=" + url).then((res) => {
        res.json().then((res) => {
            vidTitle = res.res;
        });
    });

    const title = document.getElementById("title");
    const status = document.getElementById("status");
    const dyn = document.getElementById("dyn");
    const spinner = document.getElementById("spinner");

    document.getElementById("mp3").style.display = "none";
    document.getElementById("mp4").style.display = "none";
    document.getElementById("waiting").style.display = "block";

    let startTime = new Date();
    let elapsedTime = 0;
    const runner = setInterval(() => {
        elapsedTime = new Date() - startTime;
        let minutes = Math.floor(elapsedTime / 60000);
        let seconds = Math.floor((elapsedTime % 60000) / 1000);
        document.getElementById("runtime").innerText = `${minutes.toString().padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}`;
    }, 1000);

    title.innerText = `Processing ${type}...`;
    spinner.style.display = "inline-block";
    status.innerText = "Your request is being processed.\nThis may take some time.";
    dyn.classList.remove("border-primary");
    dyn.classList.remove("border-secondary");
    dyn.classList.remove("border-danger");
    dyn.classList.add("border-warning");

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/d");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.responseType = "blob";
    xhr.send(JSON.stringify({ type: type, url: url }));

    xhr.onprogress = (e) => {
        if (xhr.status === 500) {
            unsupported();
            return;
        }
        dyn.classList.remove("border-warning");
        dyn.classList.add("border-primary");
        title.innerText = "Downloading...";
        status.innerText = "File processed. Downloading now.\nBytes processed: " + e.loaded;
    };

    xhr.onerror = () => unsupported();

    function unsupported() {
        dyn.classList.remove("border-warning");
        dyn.classList.add("border-danger");
        spinner.style.display = "none";
        title.innerText = "Error!";
        status.innerText =
            "The download operation has failed.\nYour desired file may be too large or is unsupported.\n\nmp3yt does not support downloading currently running livestreams, bulk playlists, or age-restricted videos.";
        cleanUp();
    }

    xhr.onload = () => {
        if (xhr.status === 500) {
            unsupported();
            return;
        }
        if (xhr.response.type === "application/json") {
            const reader = new FileReader();
            reader.readAsText(xhr.response);
            reader.onload = () => {
                const res = JSON.parse(reader.result);
                if (res.error || !res.res) {
                    dyn.classList.remove("border-secondary");
                    dyn.classList.add("border-danger");
                    spinner.style.display = "none";
                }
                if (res.error) {
                    title.innerText = "Invalid!";
                    status.innerText = res.error;
                    return;
                }
                if (!res.res) {
                    title.innerText = "Error!";
                    status.innerText = "The download operation has failed.";
                    const err = document.createElement("a");
                    err.innerHTML = "<br>View error";
                    err.href = "#";
                    err.onclick = () => alert(res.stderr);
                    status.appendChild(err);
                    cleanUp();
                }
            };
            return;
        }
        cleanUp();
        title.innerText = "Done!";
        dyn.classList.remove("border-primary");
        dyn.classList.add("border-success");
        spinner.style.display = "none";
        status.innerText = "Your file is ready for download.";
        const blob = new Blob([xhr.response], { type: type === "mp3" ? "audio/mpeg" : "video/mp4" });
        download(blob, vidTitle);
    };

    function cleanUp() {
        clearInterval(runner);
        document.getElementById("mp3").style.display = "block";
        document.getElementById("mp4").style.display = "block";
        document.getElementById("waiting").style.display = "none";
        document.getElementById("link").value = "";
        document.getElementById("link").disabled = false;
    }
}
