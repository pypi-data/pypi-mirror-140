import json
import logging
import os.path
import requests
import twine.package

logger = logging.getLogger(__name__)


def upload_zenodo(distribution_file, endpoint, access_token,
                  metadata=None, update=None, publish=False):
    pkg = twine.package.PackageFile.from_filename(distribution_file,
                                                  comment=None)
    pkg_meta = pkg.metadata_dictionary()
    combined_meta = {
        "upload_type": "software",
        "version": pkg_meta["version"],
        "license": pkg_meta["license"],
    }
    if metadata:
        if "description" not in metadata and pkg_meta["description"]:
            resp = requests.post(
                "https://api.github.com/markdown",
                params={"accept": "application/vnd.github.v3+json"},
                data=json.dumps({"text": pkg_meta["description"]})
            )
            if resp.ok:
                metadata["description"] = resp.content.decode()
        combined_meta.update(metadata)

    from pprint import pformat
    logger.debug(f"Metadata: {pformat(combined_meta)}")

    params = {"access_token": access_token}
    with requests.Session() as session:
        session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        if not update:
            r = session.post(f"{endpoint}/deposit/depositions",
                             params=params, json={},
                             headers={"Content-Type": "application/json"})
            logger.debug(f"Deposition created response: {pformat(r.json())}")
            deposition = f"{endpoint}/deposit/depositions/{r.json()['id']}"
        else:
            r = session.post(f"{endpoint}/deposit/depositions/{update}"
                             "/actions/newversion", params=params)
            logger.debug(f"Deposition opened for version add: {pformat(r.json())}")
            deposition = r.json()["links"]["latest_draft"]
            r = session.get(deposition, params=params)
        bucket_link = r.json()["links"]["bucket"]
        with open(distribution_file, "rb") as fp:
            r = requests.put(
                "/".join((bucket_link, os.path.basename(distribution_file))),
                data=fp, params=params)
            logger.debug(f"File upload response: {pformat(r.json())}")

        r = requests.put(deposition, params=params,
                         data=json.dumps({"metadata": combined_meta}),
                         headers={"Content-Type": "application/json"})
        logger.debug(f"Metadata edit response: {pformat(r.json())}")

        logger.info("The draft deposit can be further edited or published at "
                    + r.json()["links"]["latest_draft_html"])
        if publish:
            r = requests.post(r.json()["links"]["publish"], params=params)
            logger.debug(f"Publication response: {pformat(r.json())}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upload release to zenodo")
    parser.add_argument("file", help="Distribution file")
    parser.add_argument("--zenodo-url", default="https://zenodo.org/api",
                        help=("Zenodo API endpoint (typically "
                              "https://zenodo.org/api or "
                              "https://sandbox.zenodo.org/api)"))
    parser.add_argument("--access-token", required=True)
    parser.add_argument("--update",
                        help="ID of the deposition to add this version to")
    parser.add_argument("--metadata",
                        help="File with additional metadata for the upload")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose printout")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Reduced printout")
    parser.add_argument("--publish", action="store_true",
                        help="Publish the (updated) deposition")
    args = parser.parse_args()
    logging.basicConfig(level=(
        logging.DEBUG if args.verbose else (
            logging.WARNING if args.quiet else logging.INFO
        )
    ))
    metadata = {}
    if args.metadata:
        with open(args.metadata) as mF:
            metadata = json.load(mF)
    upload_zenodo(args.file, args.zenodo_url, args.access_token,
                  metadata=metadata, update=args.update, publish=args.publish)
