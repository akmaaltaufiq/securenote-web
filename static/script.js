function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const submitBtn = form?.querySelector("button[type='submit']");
  const clearBtn = document.getElementById("clear-btn");
  const textarea = document.querySelector("textarea");

  if (form && submitBtn && textarea) {
    form.addEventListener("submit", (e) => {
      if (!textarea.value.trim()) {
        e.preventDefault();
        textarea.style.border = "2px solid red";
        alert("Teks email tidak boleh kosong!");
      } else {
        textarea.style.border = "";
        submitBtn.innerHTML = "Memproses...";
        submitBtn.disabled = true;
      }
    });
  }

  if (clearBtn && textarea) {
    clearBtn.addEventListener("click", (e) => {
      e.preventDefault();
      textarea.value = "";
      textarea.style.border = "";
    });
  }

  const resultBox = document.querySelector(".result");
  if (resultBox) {
    resultBox.classList.add("highlight");
    setTimeout(() => {
      resultBox.classList.remove("highlight");
    }, 3000);
  }
});
