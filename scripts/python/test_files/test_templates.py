# TODO: moving tests needed since refactoring was done

# from config.templates import TemplateWrapper
#
#
# def test_init():
#     template = TemplateWrapper("test", "/path/to/root/{asset}/{step}/v{version}/{asset}.{ext}")
#     assert template._template.pattern == "/path/to/root/{asset}/{step}/v{version}/{asset}.{ext}"
#
#     template = TemplateWrapper("test", "/path/to\\root/{asset}\\{step}/v{version}/{asset}.{ext}")
#     assert template._template.pattern == "/path/to/root/{asset}/{step}/v{version}/{asset}.{ext}"
#
#     template = TemplateWrapper("test", "C:\\path/to\\root/{asset}\\{step}\\v{version}\\{asset}.{ext}")
#     assert template._template.pattern == "C:/path/to/root/{asset}/{step}/v{version}/{asset}.{ext}"
#
#
# def test_format():
#     template = TemplateWrapper("test", "/path/to/root/{asset}/{step}/v{version}/{asset}.{ext}")
#     fields = {"asset": "deer", "step": "animation", "version": "014", "ext": "abc", "ext2": ""}
#     path = template.format(fields)
#     assert path == "/path/to/root/deer/animation/v014/deer.abc"
#
#     # template = TemplateWrapper("test", "C:/Users/user/Downloads/houdini_code_assignments/cache_manager/{step}/{asset}/v{version}/{asset}.{ext}")
#     # fields = {'asset': 'testSphere.bgeo', 'ext': 'sc', 'step': 'caches', 'version': 5}
#     # path = template.format(fields)
#     # assert path == "C:/Users/user/Downloads/houdini_code_assignments/cache_manager/{step}/{asset}/v{version}/{asset}.{ext}"
#
#
# # TODO: test_parse
