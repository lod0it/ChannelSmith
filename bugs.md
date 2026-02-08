### This Document contains a list of bugs to fix and features implementation needed
{$BugDescription}[BugID]
### Bugs
✓ {once drag and dropped the image into the Unpack Texture panel the user has no feedback that the image has been uploaded}[ImageUploadFeedback]
✓ {once the channel extraction is completed, the name of the resulting textures are wrongly displayed, Ambient Occlusion / Metallic / Roughness and so on.. since we don't have any clue of which texture_map we've extracted, simply name it as its channel so Red Channel / Green Channel / Blue Channel}[ChannelNaming]