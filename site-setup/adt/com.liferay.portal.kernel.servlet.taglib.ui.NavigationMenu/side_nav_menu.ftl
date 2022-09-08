<label for="productDocumentationSelector">
	<select class="form-control" id="productDocumentationSelector">
		<#if entries?has_content>
			<#list entries as navigationEntry>
				<#assign navEntryName = navigationEntry.getName() />
				<#assign navEntryNameShort = navEntryName?replace(" /", "")?replace(" ", "-")?lower_case />

				<option value="${navEntryNameShort}">
					${languageUtil.get(locale, navEntryNameShort, navEntryName)}
				</option>
			</#list>
		</#if>
	</select>
</label>