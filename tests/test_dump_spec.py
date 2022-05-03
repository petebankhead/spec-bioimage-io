from pathlib import Path

from bioimageio.spec.shared import yaml


def test_spec_round_trip(unet2d_nuclei_broad_any_minor):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    expected = yaml.load(unet2d_nuclei_broad_any_minor)
    # monkeypatch: yaml.load already converts timestamp to datetime.datetime, while we serialize it to ISO 8601
    if "timestamp" in expected:
        expected["timestamp"] = expected["timestamp"].isoformat()

    # round-trip
    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any_minor)
    serialized = serialize_raw_resource_description_to_dict(raw_model, convert_absolute_paths=True)

    assert isinstance(serialized, dict)
    assert expected == serialized

    # as we converted absolute paths back to relative, we need to set the root path
    serialized["root_path"] = unet2d_nuclei_broad_any_minor.parent
    raw_model_from_serialized = load_raw_resource_description(serialized)
    assert raw_model_from_serialized == raw_model


def test_spec_round_trip_w_attachments(unet2d_nuclei_broad_latest):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = yaml.load(unet2d_nuclei_broad_latest)
    data["root_path"] = unet2d_nuclei_broad_latest.parent

    # monkeypatch: yaml.load already converts timestamp to datetime.datetime, while we serialize it to ISO 8601
    if "timestamp" in data:
        data["timestamp"] = data["timestamp"].isoformat()

    data["attachments"] = {"files": ["some_file.ext"], "another_unknown_attachment": ["sub", "whatever", {"weird": 10}]}

    raw_model = load_raw_resource_description(data)

    serialized = serialize_raw_resource_description_to_dict(raw_model, convert_absolute_paths=True)
    assert isinstance(serialized, dict)
    serialized["root_path"] = unet2d_nuclei_broad_latest.parent
    assert serialized == data

    raw_model_from_serialized = load_raw_resource_description(serialized)
    assert raw_model_from_serialized == raw_model


def test_dataset_rdf_round_trip(dataset_rdf):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = yaml.load(dataset_rdf)
    raw = load_raw_resource_description(data)
    serialized = serialize_raw_resource_description_to_dict(raw)
    assert data == serialized


def test_serialize_with_link_in_path(dataset_rdf, tmp_path: Path):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = load_raw_resource_description(dataset_rdf)

    true_root = tmp_path / "root"
    true_root.mkdir()
    linked_root = tmp_path / "link"
    linked_root.symlink_to(true_root)

    doc_path = linked_root / "docs.md"
    doc_path.write_text("# Documentation")

    data.root_path = true_root
    data.documentation = doc_path  # doc path only in root through link

    serialized = serialize_raw_resource_description_to_dict(data, convert_absolute_paths=True)
    assert serialized["documentation"] == "docs.md"
