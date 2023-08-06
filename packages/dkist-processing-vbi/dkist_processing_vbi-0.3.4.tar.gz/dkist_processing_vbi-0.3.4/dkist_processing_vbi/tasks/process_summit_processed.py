from astropy.io import fits
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess


class GenerateL1SummitData(WorkflowTaskBase, FitsDataMixin):
    """
    Task class for updating the headers of on-summit processed VBI data
    """

    record_provenance = True

    def run(self) -> None:
        """
        For all input frames:
            - Add data-dependent SPEC-0214 headers
            - Write out
        """
        for obj in self.fits_data_read_fits_access(
            # It's not strictly necessary to sort on "Observe" frames here because all the tags are preserved below,
            #  but this potentially drastically reduces the number of files we need to look at.
            tags=[VbiTag.input(), VbiTag.frame(), VbiTag.task("Observe")],
            cls=VbiL0FitsAccess,
        ):
            processed_hdu_list = fits.HDUList([fits.PrimaryHDU(data=obj.data, header=obj.header)])
            all_tags = self.tags(obj.name)
            all_tags.remove(VbiTag.input())
            self.fits_data_write(
                processed_hdu_list, tags=[VbiTag.calibrated(), VbiTag.stokes("I")] + all_tags
            )
