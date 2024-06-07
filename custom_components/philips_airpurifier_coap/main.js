const DOMAIN="philips_airpurifier_coap",ICON_STORE={},PREFIXES={pap:"pap"},PATH_CLASSES={"fa-primary":"primary","fa-secondary":"secondary",primary:"primary",secondary:"secondary"},preProcessIcon=async(iconSet,iconName)=>{const[icon,format]=iconName.split("#"),data=await fetch(`/${DOMAIN}/icons/${iconSet}/${icon}.svg`),text=await data.text(),parser=new DOMParser,doc=parser.parseFromString(text,"text/html");if(!doc||!doc.querySelector("svg"))return{};const viewBox=doc.querySelector("svg").getAttribute("viewBox"),_paths=doc.querySelectorAll("path"),paths={};let path="";for(const pth of _paths){path+=pth.getAttribute("d");const cls=pth.classList[0];PATH_CLASSES[cls]&&(paths[PATH_CLASSES[cls]]=pth.getAttribute("d"))}let fullCode=null;const svgEl=doc.querySelector("svg"),hasOn=Array.from(svgEl.attributes).some(a=>a.name.startsWith("on"));return hasOn||svgEl.getElementsByTagName("script").length||(fullCode=svgEl),{viewBox:viewBox,path:path,paths:paths,format:format,fullCode:fullCode}},getIcon=(iconSet,iconName)=>new Promise(async(resolve,reject)=>{const icon=`${iconSet}:${iconName}`;ICON_STORE[icon]&&resolve(ICON_STORE[icon]),ICON_STORE[icon]=preProcessIcon(iconSet,iconName),resolve(ICON_STORE[icon])}),getIconList=async iconSet=>{const data=await fetch(`/${DOMAIN}/list/${iconSet}`),text=await data.text();return JSON.parse(text)};"customIconsets"in window||(window.customIconsets={}),"customIcons"in window||(window.customIcons={}),window.customIcons.pap={getIcon:iconName=>getIcon("pap",iconName),getIconList:()=>getIconList("pap")},customElements.whenDefined("ha-icon").then(()=>{const HaIcon=customElements.get("ha-icon");HaIcon.prototype._setCustomPath=async function(promise,requestedIcon){const icon=await promise;if(requestedIcon!==this.icon)return;this._path=icon.path,this._viewBox=icon.viewBox,await this.UpdateComplete;const el=this.shadowRoot.querySelector("ha-svg-icon");if(el&&el.setPaths)if(el.clearPaths(),icon.fullCode&&"fullcolor"===icon.format){await el.updateComplete;const root=el.shadowRoot.querySelector("svg"),styleEl=document.createElement("style");styleEl.innerHTML="\n        svg:first-child>g:first-of-type>path {\n          display: none;\n        }\n      ",root.appendChild(styleEl),root.appendChild(icon.fullCode.cloneNode(!0))}else el.setPaths(icon.paths),icon.format&&el.classList.add(...icon.format.split("-"))}}),customElements.whenDefined("ha-svg-icon").then(()=>{const HaSvgIcon=customElements.get("ha-svg-icon");HaSvgIcon.prototype.clearPaths=async function(){await this.updateComplete;const svgRoot=this.shadowRoot.querySelector("svg");for(;svgRoot&&svgRoot.children.length>1;)svgRoot.removeChild(svgRoot.lastChild);const svgGroup=this.shadowRoot.querySelector("g");for(;svgGroup&&svgGroup.children.length>1;)svgGroup.removeChild(svgGroup.lastChild);for(;this.shadowRoot.querySelector("style.pap");){const el=this.shadowRoot.querySelector("style.pap");el.parentNode.removeChild(el)}},HaSvgIcon.prototype.setPaths=async function(paths){if(await this.updateComplete,null==paths||0===Object.keys(paths).length)return;const styleEl=this.shadowRoot.querySelector("style.pap")||document.createElement("style");styleEl.classList.add("pap"),styleEl.innerHTML="\n      .secondary {\n        opacity: 0.4;\n      }\n      :host(.invert) .secondary {\n        opacity: 1;\n      }\n      :host(.invert) .primary {\n        opacity: 0.4;\n      }\n      :host(.color) .primary {\n        opacity: 1;\n      }\n      :host(.color) .secondary {\n        opacity: 1;\n      }\n      :host(.color:not(.invert)) .secondary {\n        fill: var(--icon-secondary-color, var(--disabled-text-color));\n      }\n      :host(.color.invert) .primary {\n        fill: var(--icon-secondary-color, var(--disabled-text-color));\n      }\n      path:not(.primary):not(.secondary) {\n        opacity: 0;\n      }\n      ",this.shadowRoot.appendChild(styleEl);const root=this.shadowRoot.querySelector("g");for(const k in paths){const el=document.createElementNS("http://www.w3.org/2000/svg","path");el.setAttribute("d",paths[k]),el.classList.add(k),root.appendChild(el)}}});