<style>
    <#include "${templatesPath}/LEARN-STYLES">
</style>
<#include "${templatesPath}/SVG">

<div class="container-fluid documentations main-content" role="main">
	<div class="row">
		<div class="col-12 p-0 page-alert" id="pageAlertContainer">
    		<div class="page-alert-hidden" id="pageAlert" role="alert">
				<@clay["alert"]
					message=languageUtil.get(locale, "important-as-we-revamp-and-transition-our-documentation-to-this-site", "<strong class=\"lead\">IMPORTANT: </strong>As we revamp and transition our documentation to this site, you may find the articles you need on <a href=\"https://help.liferay.com/hc\"><strong>Liferay's Help Center</strong></a>.")
					displayType="info"
					defaultTitleDisabled=true
					dismissible=true
				/>
			</div>
		</div>

		<div class="col-12 col-md-2 doc-nav-wrapper mobile-nav-hide">
			<div class="doc-nav-wrapper-inner">
				<div class="info-bar">
					<label for="productDocumentationSelector">
						<select class="form-control" id="productDocumentationSelector">
							<option value="analytics-cloud">
								{% trans %}Analytics Cloud{% endtrans %}
							</option>
							<option value="commerce">
								{% trans %}Commerce{% endtrans %}
							</option>
							<option value="dxp">
								{% trans %}DXP / Portal{% endtrans %}
							</option>
							<option value="dxp-cloud">
								{% trans %}DXP Cloud{% endtrans %}
							</option>
							<option value="reference">
								{% trans %}Reference{% endtrans %}
							</option>
						</select>
					</label>
				</div>

				<div class="d-md-none mobile-doc-nav-toggler" id="mobileDocNavToggler">{% trans %}Documentation Menu{%
					endtrans %}
					<button aria-label="Expand Documentation Menu" class="btn expand-btn" onclick="javascript:;"
						title="Expand Documentation Menu" type="button">
						<svg class="lexicon-icon lexicon-icon-product-menu" role="presentation">
							<use xlink:href="#product-menu" />
						</svg>
					</button>

					<button aria-label="Close Documentation Menu" class="btn collapse-btn" onclick="javascript:;"
						title="Close Documentation Menu" type="button">
						<svg class="lexicon-icon lexicon-icon-times" role="presentation">
							<use xlink:href="#times" />
						</svg>
					</button>
				</div>

				<div class="doc-nav">
					{% include "highlighting-alert.html" %}

					{% if parents|length > 0 %}
					{% set backURL %}
					{%- for doc in parents -%}
					{% if loop.last %}
					{{ doc.link|e }}
					{% endif %}
					{%- endfor -%}
					{% endset %}

					{% set backURL = backURL.replace("README", "index") %}

					<a class="back-link btn btn-monospaced btn-link" href="{{ backURL }}" id="backLink">
						<svg class="lexicon-icon lexicon-icon-angle-left" role="presentation" viewBox="0 0 512 512">
							<use xlink:href="#angle-left" />
						</svg>
						{% trans %}Go Back{% endtrans %}
					</a>
					{% endif %}

					{% block sidebar1 %}
					<#if (Navigation.getData())??>
						${Navigation.getData()}
					</#if>
					{% endblock %}
				</div>

				<div class="d-none d-md-flex doc-nav-footer">
                    <@liferay_ui["language"]
                        ddmTemplateKey="LANGUAGE_MENU"
                        ddmTemplateGroupId=groupId
                        displayCurrentLocale=true
                        languageIds=localeUtil.toLanguageIds(languageUtil.getAvailableLocales(themeDisplay.getSiteGroupId()))
                        useNamespace=false
				    />
				</div>
			</div>
		</div>

		<div class="col-12 col-md-10 doc-body">
			<div class="col-12 general-info p-0">
				<div class="col-12 info-bar">
					<div class="breadcrumb-wrapper col-12 col-md-7 offset-md-1">
						{% include "breadcrumb.html" %}
						<#if (Breadcrumb.getData())??>
							${Breadcrumb.getData()}
						</#if>
					</div>

					<div class="actions col-md-2 d-none d-md-block offset-md-1">
						<a aria-label="${languageUtil.get(locale, 'github-icon', 'Github Icon')}"
							href="<#if (githubEditLink.getData())??> ${githubEditLink.getData()}</#if>"
							title="${languageUtil.get(locale, 'contribute-on-github', 'Contribute on Github')}">
							<svg>
								<use xlink:href="#edit"></use>
							</svg>
						</a>
					</div>
				</div>
			</div>

			<div class="col-12 doc-content" id="docContent">
				<div class="row">
					<div class="article-body col-12 col-md-8">
						<#if (Body.getData())??>
							${Body.getData()}
						</#if>
						<div class="autofit-padded-no-gutters-x autofit-row help-center-footer">
                            <div class="autofit-col">
                                <div class="icon-container">
                                    <svg class="lexicon-icon liferay-waffle-icon" focusable="false" role="presentation" viewBox="0 0 512 512">
                                        <use xlink:href="#liferay-waffle" />
                                    </svg>
                                </div>
                            </div>

                            <div class="autofit-col autofit-col-expand">
                                <h3>${languageUtil.get(locale, "not-finding-what-you-are-looking-for", "Not finding what you're looking for?")}</h3>

                                <p class="text-secondary">${languageUtil.get(locale, "pardon-our-dust-as-we-revamp", "Pardon our dust as we revamp and transition our product documentation to this site. If something seems missing, please check Liferay Help Center documentation for Liferay DXP 7.2 and previous versions.")}</p>

                                <a href="https://help.liferay.com/hc/en-us/categories/360001749912">
                                    <strong>${languageUtil.get(locale, "try-liferays-help-center", "Try Liferay's Help Center")}</strong>

                                    <svg class="lexicon-icon lexicon-icon-shortcut" focusable="false" role="presentation" viewBox="0 0 512 512">
                                        <use xlink:href="#shortcut" />
                                    </svg>
                                </a>
                            </div>
                        </div>
					</div>

					<div class="col-md-4 d-none d-sm-block toc-container">
						<ul class="nav nav-stacked toc" id="articleTOC"></ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<#attempt>
	<script>
		// Table of contents reading indicator

		const headings = document.querySelectorAll('.article-body h2');

		let activeIndex;
		let targets = [];

		if (headings) {
			const articleTOC = document.getElementById('articleTOC');

			headings.forEach(
				heading => {
					const id = heading.querySelector('a').hash.replace('#', '');

					if (articleTOC) {
						articleTOC.innerHTML += `
                    <li class="nav-item">
                        <a class="nav-link" id="toc-${id}" href="#${id}">
                            ${heading.innerText}
                        </a>
                    </li>`;
					}

					targets.push({ id: id, isIntersecting: false });
				}
			);
		}

		const callback = entries => {
			entries.forEach(entry => {
				const index = targets.findIndex(target => target.id === entry.target.id);

				targets[index].isIntersecting = entry.isIntersecting;

				if (!targets[activeIndex] || !targets[activeIndex].isIntersecting) {
					setActiveIndex()
				}
			});

			if (targets[activeIndex]) {
				toggleActiveClass(targets[activeIndex].id);
			}
		};

		// rootMargin of 157px is header height + info bar height + 24px gutter offset

		const observer = new IntersectionObserver(callback, { rootMargin: '-157px', threshold: [0, 0.2, 0.4, 0.6, 0.8, 1] });

		const setActiveIndex = () => {
			activeIndex = targets.findIndex(target => target.isIntersecting === true);
		};

		const toggleActiveClass = id => {
			targets.forEach(target => {
				const node = document.getElementById(`toc-${target.id}`);

				if (node) {
					node.classList.remove('active');
				}
			});

			const activeNode = document.getElementById(`toc-${id}`);

			if (activeNode) {
				activeNode.classList.add('active');
			}
		}

		targets.forEach(target => {
			const node = target.id ? document.getElementById(target.id) : null;

			if (node) {
				observer.observe(node);

				node.style.cssText = "margin-top: -157px; padding-top: 157px;"
			}
		});

		// Documentation dropdown

		const breadcrumbAncestor = document.querySelector('.breadcrumb-parent');
		const breadcrumbCurrentArticle = document.getElementById('breadcrumbCurrentArticle');

		const productDocumentationSelector = document.getElementById('productDocumentationSelector');

		if (breadcrumbCurrentArticle && productDocumentationSelector) {

			// Preselect documentation dropdown to be the current article's product

			const currentDocProduct = breadcrumbAncestor ? breadcrumbAncestor : breadcrumbCurrentArticle;

			const currentDocProductValue = currentDocProduct.innerText.replace(/\s/g, '-').toLowerCase();

			productDocumentationSelector.value = currentDocProductValue;

			// Route user to the selected documentation landing page

			productDocumentationSelector.addEventListener('change', event => {
				const target = event.target.value;

				if (target !== currentDocProductValue) {
					if (target === 'analytics-cloud') {
						window.location.pathname = '/analytics-cloud/latest/en/index.html';
					} else if (target === 'commerce') {
						window.location.pathname = '/commerce/latest/en/index.html';
					} else if (target === 'dxp-cloud') {
						window.location.pathname = '/dxp-cloud/latest/en/index.html';
					} else if (target === 'reference') {
						window.location.pathname = '/reference/latest/en/index.html';
					} else {
						window.location.pathname = '/dxp/latest/en/index.html';
					}
				}
			});
		}

		// Left nav interaction

		const activeNavL1 = document.querySelector('.toctree-l1.current');

		const checkDescendantLevel = (level, lastActiveItem) => {
			const grandparent = document.querySelector(`.toctree-l${level - 2}.current`);
			const parent = lastActiveItem || document.querySelector(`.toctree-l${level - 1}.current`);
			const parentSiblings = document.querySelectorAll(`.toctree-l${level - 1}:not(.current)`);

			const currentLevel = parent ?
				parent.querySelectorAll(`li.toctree-l${level}`) :
				document.querySelectorAll(`li.toctree-l${level}`);

			if (currentLevel.length) {
				let activeItem = null;

				grandparent ? grandparent.querySelector('a').classList.add('d-none') : '';
				parentSiblings.forEach(node => node.classList.add('d-none'));
				parent ? parent.classList.add('parent-level') : '';

				currentLevel.forEach(node => {
					if (node.classList.contains('current')) {
						activeItem = node;
					}
				})

				if (activeItem) {
					level++;

					checkDescendantLevel(level, activeItem);
				} else {
					return;
				}
			}
		}

		if (activeNavL1) {
			checkDescendantLevel(1);
		}

		// Left Nav mobile interaction

		const docNavWrapper = document.querySelector('.doc-nav-wrapper');
		const mobileDocNavToggler = document.getElementById('mobileDocNavToggler');

		if (docNavWrapper && mobileDocNavToggler) {
			const togglers = mobileDocNavToggler.querySelectorAll('button');

			togglers.forEach(toggler =>
				toggler.addEventListener('click', () => {
					docNavWrapper.classList.toggle('mobile-nav-hide');
				})
			);
		}
	</script>
	<#recover>
		<div>script error</div>
</#attempt>

<script>
    <#include "${templatesPath}/PAGE-ALERT-JS">
</script>