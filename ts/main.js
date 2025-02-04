(() => {
    // PhotoSwipe 圖庫類別
    var g = class e {
      galleryUID;
      items = [];
  
      constructor(t, r = 1) {
        // 如果沒有 PhotoSwipe，就顯示錯誤並返回
        if (window.PhotoSwipe == null || window.PhotoSwipeUI_Default == null) {
          console.error("PhotoSwipe lib not loaded.");
          return;
        }
        this.galleryUID = r;
  
        e.createGallery(t);
        this.loadItems(t);
        this.bindClick();
      }
  
      loadItems(t) {
        this.items = [];
        let r = t.querySelectorAll("figure.gallery-image");
        for (let i of r) {
          let n = i.querySelector("figcaption"),
              o = i.querySelector("img"),
              s = {
                w: parseInt(o.getAttribute("width")),
                h: parseInt(o.getAttribute("height")),
                src: o.src,
                msrc: o.getAttribute("data-thumb") || o.src,
                el: i
              };
          n && (s.title = n.innerHTML);
          this.items.push(s);
        }
      }
  
      static createGallery(t) {
        let r = t.querySelectorAll("img.gallery-image");
        for (let o of Array.from(r)) {
          let s = o.closest("p");
          if (!s || !t.contains(s) || (s.textContent.trim() == "" && s.classList.add("no-text"), !s.classList.contains("no-text"))) continue;
  
          let d = o.parentElement.tagName == "A",
              m = o,
              a = document.createElement("figure");
          a.style.setProperty("flex-grow", o.getAttribute("data-flex-grow") || "1");
          a.style.setProperty("flex-basis", o.getAttribute("data-flex-basis") || "0");
  
          // 如果原本是 <a><img/></a> 包起來
          d && (m = o.parentElement);
  
          m.parentElement.insertBefore(a, m);
          a.appendChild(m);
  
          if (o.hasAttribute("alt")) {
            let l = document.createElement("figcaption");
            l.innerText = o.getAttribute("alt");
            a.appendChild(l);
          }
  
          if (!d) {
            a.className = "gallery-image";
            let l = document.createElement("a");
            l.href = o.src;
            l.setAttribute("target", "_blank");
            o.parentNode.insertBefore(l, o);
            l.appendChild(o);
          }
        }
  
        let i = t.querySelectorAll("figure.gallery-image"),
            n = [];
        for (let o of i) {
          n.length
            ? o.previousElementSibling === n[n.length - 1]
              ? n.push(o)
              : n.length && (e.wrap(n), (n = [o]))
            : (n = [o]);
        }
        n.length > 0 && e.wrap(n);
      }
  
      static wrap(t) {
        let r = document.createElement("div");
        r.className = "gallery";
        let i = t[0].parentNode,
            n = t[0];
        i.insertBefore(r, n);
        for (let o of t) r.appendChild(o);
      }
  
      open(t) {
        let r = document.querySelector(".pswp");
        new window.PhotoSwipe(
          r,
          window.PhotoSwipeUI_Default,
          this.items,
          {
            index: t,
            galleryUID: this.galleryUID,
            getThumbBoundsFn: (n) => {
              let o = this.items[n].el.getElementsByTagName("img")[0],
                  s = window.pageYOffset || document.documentElement.scrollTop,
                  c = o.getBoundingClientRect();
              return { x: c.left, y: c.top + s, w: c.width };
            }
          }
        ).init();
      }
  
      bindClick() {
        for (let [t, r] of this.items.entries()) {
          r.el.querySelector("a").addEventListener("click", (n) => {
            n.preventDefault();
            this.open(t);
          });
        }
      }
    };
    var b = g;
  
    // Node Vibrant 快取物件（用於文章封面取色）
    var u = {};
    if (localStorage.hasOwnProperty("StackColorsCache")) {
      try {
        u = JSON.parse(localStorage.getItem("StackColorsCache"));
      } catch {
        u = {};
      }
    }
  
    // 取色函式
    async function S(e, t, r) {
      if (!e) return await Vibrant.from(r).getPalette();
      if (!u.hasOwnProperty(e) || u[e].hash !== t) {
        let i = await Vibrant.from(r).getPalette();
        u[e] = {
          hash: t,
          Vibrant: {
            hex: i.Vibrant.hex,
            rgb: i.Vibrant.rgb,
            bodyTextColor: i.Vibrant.bodyTextColor
          },
          DarkMuted: {
            hex: i.DarkMuted.hex,
            rgb: i.DarkMuted.rgb,
            bodyTextColor: i.DarkMuted.bodyTextColor
          }
        };
        localStorage.setItem("StackColorsCache", JSON.stringify(u));
      }
      return u[e];
    }
  
    // SlideUp / SlideDown
    var D = (e, t = 500) => {
      e.classList.add("transiting");
      e.style.transitionProperty = "height, margin, padding";
      e.style.transitionDuration = t + "ms";
      e.style.height = e.offsetHeight + "px";
      e.offsetHeight;
      e.style.overflow = "hidden";
      e.style.height = "0";
      e.style.paddingTop = "0";
      e.style.paddingBottom = "0";
      e.style.marginTop = "0";
      e.style.marginBottom = "0";
      window.setTimeout(() => {
        e.classList.remove("show");
        e.style.removeProperty("height");
        e.style.removeProperty("padding-top");
        e.style.removeProperty("padding-bottom");
        e.style.removeProperty("margin-top");
        e.style.removeProperty("margin-bottom");
        e.style.removeProperty("overflow");
        e.style.removeProperty("transition-duration");
        e.style.removeProperty("transition-property");
        e.classList.remove("transiting");
      }, t);
    };
  
    var q = (e, t = 500) => {
      e.classList.add("transiting");
      e.style.removeProperty("display");
      e.classList.add("show");
      let r = e.offsetHeight;
      e.style.overflow = "hidden";
      e.style.height = "0";
      e.style.paddingTop = "0";
      e.style.paddingBottom = "0";
      e.style.marginTop = "0";
      e.style.marginBottom = "0";
      e.offsetHeight;
      e.style.transitionProperty = "height, margin, padding";
      e.style.transitionDuration = t + "ms";
      e.style.height = r + "px";
      e.style.removeProperty("padding-top");
      e.style.removeProperty("padding-bottom");
      e.style.removeProperty("margin-top");
      e.style.removeProperty("margin-bottom");
      window.setTimeout(() => {
        e.style.removeProperty("height");
        e.style.removeProperty("overflow");
        e.style.removeProperty("transition-duration");
        e.style.removeProperty("transition-property");
        e.classList.remove("transiting");
      }, t);
    };
  
    var B = (e, t = 500) =>
      window.getComputedStyle(e).display === "none" ? q(e, t) : D(e, t);
  
    // 漢堡選單
    function v() {
      let e = document.getElementById("toggle-menu");
      if (!e) return;
      e.addEventListener("click", () => {
        let menu = document.getElementById("main-menu");
        if (menu.classList.contains("transiting")) return;
        document.body.classList.toggle("show-menu");
        B(menu, 300);
        e.classList.toggle("is-active");
      });
    }
  
    // createElement 工具函式
    function N(e, t, r) {
      var i = document.createElement(e);
      for (let n in t)
        if (n && t.hasOwnProperty(n)) {
          let o = t[n];
          if (n == "dangerouslySetInnerHTML") {
            i.innerHTML = o.__html;
          } else {
            o === true
              ? i.setAttribute(n, n)
              : o !== false && o != null && i.setAttribute(n, o.toString());
          }
        }
      for (let n = 2; n < arguments.length; n++) {
        let o = arguments[n];
        o && i.appendChild(o.nodeType == null ? document.createTextNode(o.toString()) : o);
      }
      return i;
    }
    var w = N;
  
    // [移除註解] ======= 移除 Dark Mode class y & var E = y; =======
    // 以下為原本的深色模式類別:
    // var y=class { ... }, E=y;
    // 以及後續 new E(...) 呼叫
    // 已整段刪除
  
    // requestAnimationFrame 包裝
    function p(e) {
      let t;
      return () => {
        t && window.cancelAnimationFrame(t);
        t = window.requestAnimationFrame(() => e());
      };
    }
  
    // TOC 高亮
    var O = ".article-content h1[id], .article-content h2[id], .article-content h3[id], .article-content h4[id], .article-content h5[id], .article-content h6[id]",
        T = "#TableOfContents",
        L = "#TableOfContents li",
        k = "active-class";
  
    function V(e, t) {
      let r = e.querySelector("a").offsetHeight,
          i = e.offsetTop - t.offsetHeight / 2 + r / 2 - t.offsetTop;
      i < 0 && (i = 0);
      t.scrollTo({ top: i, behavior: "smooth" });
    }
  
    function U(e) {
      let t = {};
      e.forEach((r) => {
        let n = r.querySelector("a").getAttribute("href");
        n.startsWith("#") && (t[n.slice(1)] = r);
      });
      return t;
    }
  
    function C(e) {
      let t = [];
      e.forEach((r) => {
        t.push({ id: r.id, offset: r.offsetTop });
      });
      t.sort((r, i) => r.offset - i.offset);
      return t;
    }
  
    function M() {
      let e = document.querySelectorAll(O);
      if (!e) {
        console.warn("No header matched query", e);
        return;
      }
      let t = document.querySelector(T);
      if (!t) {
        console.warn("No toc matched query", T);
        return;
      }
      let r = document.querySelectorAll(L);
      if (!r) {
        console.warn("No navigation matched query", L);
        return;
      }
      let i = C(e),
          n = false;
      t.addEventListener("mouseenter", p(() => (n = true)));
      t.addEventListener("mouseleave", p(() => (n = false)));
  
      let o,
          s = U(r);
      function c() {
        let m = document.documentElement.scrollTop || document.body.scrollTop,
            a;
        i.forEach((f) => {
          m >= f.offset - 20 && (a = document.getElementById(f.id));
        });
        let l;
        if (a && (l = s[a.id]), a && !l) {
          console.debug("No link found for section", a);
        } else if (l !== o) {
          o && o.classList.remove(k);
          if (l) {
            l.classList.add(k);
            !n && V(l, t);
          }
          o = l;
        }
      }
      window.addEventListener("scroll", p(c));
      function d() {
        i = C(e);
        c();
      }
      window.addEventListener("resize", p(d));
    }
  
    // 錨點平滑滾動
    var $ = "a[href]";
    function P() {
      document.querySelectorAll($).forEach((e) => {
        e.getAttribute("href").startsWith("#") &&
          e.addEventListener("click", (r) => {
            r.preventDefault();
            let i = decodeURI(e.getAttribute("href").substring(1)),
                n = document.getElementById(i),
                o = n.getBoundingClientRect().top - document.documentElement.getBoundingClientRect().top;
            window.history.pushState({}, "", e.getAttribute("href"));
            scrollTo({ top: o, behavior: "smooth" });
          });
      });
    }
  
    // Stack 全域物件
    var x = {
      init: () => {
        // 漢堡選單
        v();
  
        // 如果有 article-content，啟用 PhotoSwipe + TOC 高亮
        let e = document.querySelector(".article-content");
        if (e) {
          new b(e);
          P();
          M();
        }
  
        // 文章列表中若為 .article-list--tile，使用 IntersectionObserver + Node Vibrant
        let t = document.querySelector(".article-list--tile");
        if (t) {
          new IntersectionObserver(async (s, c) => {
            s.forEach((d) => {
              if (!d.isIntersecting) return;
              c.unobserve(d.target);
              d.target.querySelectorAll("article.has-image").forEach(async (a) => {
                let l = a.querySelector("img"),
                    f = l.src,
                    H = l.getAttribute("data-key"),
                    I = l.getAttribute("data-hash"),
                    A = a.querySelector(".article-details"),
                    h = await S(H, I, f);
                A.style.background = `
                          linear-gradient(0deg,
                              rgba(${h.DarkMuted.rgb[0]}, ${h.DarkMuted.rgb[1]}, ${h.DarkMuted.rgb[2]}, 0.5) 0%,
                              rgba(${h.Vibrant.rgb[0]}, ${h.Vibrant.rgb[1]}, ${h.Vibrant.rgb[2]}, 0.75) 100%)
                      `;
              });
            });
          }).observe(t);
        }
  
        // 代碼塊 Copy 按鈕
        let r = document.querySelectorAll(".article-content div.highlight"),
            i = "Copy",
            n = "Copied!";
        r.forEach((o) => {
          let s = document.createElement("button");
          s.innerHTML = i;
          s.classList.add("copyCodeButton");
          o.appendChild(s);
  
          let c = o.querySelector("code[data-lang]");
          c &&
            s.addEventListener("click", () => {
              navigator.clipboard
                .writeText(c.textContent)
                .then(() => {
                  s.textContent = n;
                  setTimeout(() => {
                    s.textContent = i;
                  }, 1000);
                })
                .catch((d) => {
                  alert(d);
                  console.log("Something went wrong", d);
                });
            });
        });
  
        // [移除註解] 2. 移除 new E(document.getElementById("dark-mode-toggle"))
        // 即不再初始化任何深色模式切換
        // new E(document.getElementById("dark-mode-toggle"));
      }
    };
  
    // DOM 加載後延遲執行 init
    window.addEventListener("load", () => {
      setTimeout(function () {
        x.init();
      }, 0);
    });
  
    // 暴露全域
    window.Stack = x;
    window.createElement = w;
  })();
  
  
/*!
*   Hugo Theme Stack
*
*   @author: Jimmy Cai
*   @website: https://jimmycai.com
*   @link: https://github.com/CaiJimmy/hugo-theme-stack
*/
