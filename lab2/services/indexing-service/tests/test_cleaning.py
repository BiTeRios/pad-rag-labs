from indexing_service.preprocessing.cleaning import clean_markdown
from indexing_service.preprocessing.normalization import normalize_text


def process(raw: str) -> str:
    return normalize_text(clean_markdown(raw))


def test_front_matter_and_html_comments_removed():
    text = process("---\ntitle: Pods\nweight: 10\n---\n<!-- overview -->\nPods are small.\n<!-- body -->\n")
    assert text == "Pods are small."


def test_glossary_tooltip_keeps_visible_text():
    raw = 'A group of {{< glossary_tooltip text="containers" term_id="container" >}} with storage.'
    assert process(raw) == "A group of containers with storage."
    assert process('Stored in {{< glossary_tooltip term_id="etcd" >}}.') == "Stored in etcd."


def test_callout_shortcodes_become_labels_and_keep_content():
    raw = "{{< note >}}\nPods are ephemeral.\n{{< /note >}}\n\n{{< warning >}}\nBe careful.\n{{< /warning >}}"
    assert process(raw) == "Note: Pods are ephemeral.\n\nWarning: Be careful."


def test_feature_state_and_heading_shortcodes_rendered():
    raw = (
        '{{< feature-state for_k8s_version="v1.29" state="stable" >}}\n\n'
        '{{< feature-state feature_gate_name="SidecarContainers" >}}\n\n'
        '## {{% heading "prerequisites" %}}\n\n## {{% heading "whatsnext" %}}'
    )
    assert process(raw) == (
        "Feature state: Kubernetes v1.29 [stable]\n\nFeature gate: SidecarContainers\n\n"
        "## Before you begin\n\n## What's next"
    )


def test_comment_and_mermaid_blocks_dropped_with_content():
    raw = "Keep.\n\n{{< comment >}}\nTODO internal\n{{< /comment >}}\n\n{{< mermaid >}}\ngraph LR; A-->B\n{{< /mermaid >}}"
    assert process(raw) == "Keep."


def test_unavailable_includes_dropped_and_code_sample_referenced():
    raw = '{{< include "task-tutorial-prereqs.md" >}} {{< version-check >}}\n\n{{< code_sample file="pods/simple-pod.yaml" >}}'
    assert process(raw) == "Example manifest: pods/simple-pod.yaml"


def test_highlight_shortcode_becomes_code_block():
    raw = '{{< highlight yaml "linenos=inline" >}}\nkind: Pod\n{{< /highlight >}}'
    assert process(raw) == "```yaml\nkind: Pod\n```"


def test_links_images_and_emphasis_stripped():
    raw = "See [Services](/docs/concepts/services/) and ![diagram](/img.svg). _Pods_ are **important**."
    assert process(raw) == "See Services and diagram. Pods are important."


def test_emphasis_across_line_break_and_heading_anchor_removed():
    raw = "### PostBind {#post-bind}\n\nIf so, **the remaining bind\nplugins are skipped**."
    assert process(raw) == "### PostBind\n\nIf so, the remaining bind plugins are skipped."


def test_html_tags_removed_but_placeholders_and_code_kept():
    raw = "Run `kubectl logs <pod-name>` or <code>kubectl get pods</code>.<br>Then use &lt;name&gt; and <your-namespace>."
    # <br> внутри абзаца — тот же абзац, нормализация склеивает строки
    assert process(raw) == "Run `kubectl logs <pod-name>` or kubectl get pods. Then use <name> and <your-namespace>."


def test_html_table_becomes_markdown_rows():
    raw = "<table>\n<tr>\n<th>Name</th>\n<th>Port</th>\n</tr>\n<tr><td>kubelet</td><td><code>10250</code></td></tr>\n</table>"
    assert process(raw) == "| Name | Port |\n| kubelet | 10250 |"


def test_code_block_content_untouched():
    raw = "Example:\n\n```yaml\nspec:\n  containers:\n  - name: <name>   # [link](x) **bold**\n```\n"
    assert process(raw) == "Example:\n\n```yaml\nspec:\n  containers:\n  - name: <name>   # [link](x) **bold**\n```"


def test_shortcodes_inside_code_rendered():
    raw = "```shell\ncurl -LO https://dl.k8s.io/release/v{{< skew currentVersion >}}/bin\n```"
    assert process(raw) == "```shell\ncurl -LO https://dl.k8s.io/release/v<version>/bin\n```"


def test_normalization_unicode_and_whitespace():
    raw = "Smart “quotes” and​ ﬁle   names\t here.  \r\n\r\n\r\n\r\nNext."
    assert normalize_text(raw) == 'Smart "quotes" and file names here.\n\nNext.'


def test_normalization_unwraps_paragraphs_but_keeps_structure():
    raw = "A Pod is a group\nof containers.\n\n## Heading\nText\n- item one\n  continued\n- item two\n| a | b |\n| c | d |"
    assert normalize_text(raw) == (
        "A Pod is a group of containers.\n\n## Heading\nText\n- item one continued\n- item two\n| a | b |\n| c | d |"
    )
