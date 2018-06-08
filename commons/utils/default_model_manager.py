from bson.objectid import ObjectId
from pymodm.manager import Manager
from pymongo.collection import ReturnDocument


class DefaultManager(Manager):

    def get_all(self, filters=None, queries=None, projection=None, limit=None, offset=None, sort=None):
        """Lists all model documents matching method args

        Queries on a specific collection and gets documents according to method args.

        Args:
            filters: list of dicts having filters.
            queries: dictionary of parameters to find the required documents.
            projection: dict of projection.
            limit: integer limit for pagination.
            offset: integer offset for pagination.
            sort: a list of dictionary which specifies the parameters and order to sort the result data.

        Returns:
            A list of model dictionaries matching the query.
        """
        query = {}
        if queries:
            query = queries

        elif filters:
            query = {
                "$and": filters
            }
        resources = self.model.objects.raw(query)
        if projection:
            resources = resources.project(projection)

        if sort:
            resources = resources.order_by(sort)

        if offset:
            resources = resources.skip(offset)

        if limit:
            resources = resources.limit(limit)
        return list(resources.values())

    def get_by_id(self, _id, projection=None):
        """Lists a single model document matching ObjectId.

        Queries on a specific collection and gets a single document according to ObjectId(_id).

        Args:
            _id: ObjectId of the document.
            projection: dict of projection required.

        Returns:
            A single model dictionary matching the ObjectId.
        """

        result = self.model.objects.raw({'_id': ObjectId(_id)})
        if projection:
            result = result.project(projection)
        try:
            result = result.values().first()
        except self.model.DoesNotExist:
            result = None
        return result

    def get_one(self, queries=None, filters=None, projection=None):
        """Lists a single model document matching the args.

        Queries on a specific collection and gets a single document according to queries or filters given.

        Args:
            filters: list of dicts having filters.
            queries: dictionary of parameters to find the required documents.
            projection: dict of projection required.

        Returns:
            A single model document matching the queries or filters.
        """

        query = {}
        if queries:
            query = queries

        elif filters:
            query = {
                "$and": filters
            }

        result = self.model.objects.raw(query)

        if projection:
            result = result.project(projection)
        try:
            result = result.values().first()
        except self.model.DoesNotExist:
            result = None

        return result

    def insert_one(self, data):
        """Inserts a single model document matching id.

        Inserts a new model document after validating the fields in data dict.

        Args:
            data: dict of data for the specific model

        Returns:
            A single resource document matching the id.
        """

        new_resource = self.model.from_document(data)
        return new_resource.save().to_son().to_dict()

    def insert_many(self, data):
        """Inserts multiple model documents

        Inserts new model documents list after validating the fields in each doc of data list.

        Args:
            data: list of dictionaries of data for the specific model

        Returns:
            Insert Many response containing list of ids of the saved documents
        """
        new_resources = [self.model.from_document(doc) for doc in data]

        response = self.model.objects.bulk_create(new_resources, full_clean=True)
        return response

    def update_one(self, data, filters=None, projection=None, upsert=False, queries=None, return_document=None):
        """Updates a single document matching query criteria.

        Updates the model document with the new data after finding it with filters.

        Args:
            filters: array of data to find the matching document
            queries: dictionary of parameters to find the matching document.
            data: dict of data that will replace old data
            projection: projection of data dict to be returned after updating.
                        DO NOT USE $ in projection please use $elemMatch
            upsert: If set to True it inserts the document if it's not already present otherwise does nothing
            return_document: If given the value of ReturnDocument.BEFORE it returns document before update is done
                    else if given the value of ReturnDocument.AFTER it returns document after the update is done

        Returns:
            The document after it is updated or before it is updated according to the value of return_document passed.
        """
        query = {}
        return_document_query = {}
        id_doc = None
        response = None
        return_document_response = None

        if queries:
            query = queries

        elif filters:
            query = {
                "$and": filters
            }

        try:
            id_doc = self.model.objects.raw(query).first()._qs.raw_query
            return_document_query = dict(id_doc)
        except Exception:
            id_doc = None
            return_document_query = dict(query)

        if id_doc:
            query_list = []
            query_list.append(id_doc)
            if '$and' not in list(query):
                for key, value in query.iteritems():
                    key_value_dict = {key: value}
                    query_list.append(key_value_dict)

                query = {}
                query.setdefault('$and', []).extend(query_list)
        elif return_document is None and not upsert:
            return 0
        elif return_document is not None and not upsert:
            return None

        queryset = self.model.objects.raw(query)
        return_doc_queryset = self.model.objects.raw(return_document_query)

        if return_document == ReturnDocument.BEFORE:
            try:
                return_document_response = return_doc_queryset
                if projection:
                    return_document_response = return_document_response.project(projection)
                return_document_response = return_document_response.values().first()
            except Exception:
                return_document_response = None

        update_response = queryset.update(data, upsert=upsert)

        if return_document == ReturnDocument.AFTER:
            try:
                return_document_response = return_doc_queryset
                if projection:
                    return_document_response = return_document_response.project(projection)
                return_document_response = return_document_response.values().first()
            except Exception:
                return_document_response = None

        if return_document is not None:
            response = return_document_response
        else:
            response = update_response
        return response

    def update_by_id(self, _id, data, projection=None, upsert=False, return_document=None):
        """Updates a single document matching query criteria.

        Updates the model document with the new data after finding it with filters.

        Args:
            data: dict of data that will replace old data.
            _id: ObjectId of the doc to be updated.
            projection: projection of data dict to be returned after updating.
            upsert: If set to True it inserts the document if it's not already present otherwise does nothing.
            return_document: If given the value of ReturnDocument.BEFORE it returns document before update is done
                    else if given the value of ReturnDocument.AFTER it returns document after the update is done.

        Returns:
            The document after it is updated or before it is updated according to the value of return_document passed.
        """
        response = None
        return_document_response = None

        queryset = self.model.objects.raw({'_id': ObjectId(_id)})

        if return_document == ReturnDocument.BEFORE:
            try:
                return_document_response = queryset
                if projection:
                    return_document_response = return_document_response.project(projection)
                return_document_response = return_document_response.values().first()
            except Exception:
                return_document_response = None

        update_response = queryset.update(data, upsert=upsert)

        if return_document == ReturnDocument.AFTER:
            try:
                return_document_response = queryset
                if projection:
                    return_document_response = return_document_response.project(projection)
                return_document_response = return_document_response.values().first()
            except Exception:
                return_document_response = None

        if return_document:
            response = return_document_response
        else:
            response = update_response
        return response

    def update_many(self, data, filters=None, queries=None, upsert=False):
        """Updates all the documents matching query criteria.

        Updates the model documents with the new data after finding them with filters.

        Args:
            filters: array of data to find the matching documents
            queries: dictionary of parameters to find the matching documents.
            data: dict of data that will replace old data
            upsert: If set to True it inserts the document if it's not already present otherwise does nothing

        Returns:
            The count of matched and modified documents.
        """
        query = {}

        if queries:
            query = queries

        elif filters:
            query = {
                "$and": filters
            }

        queryset = self.model.objects.raw(query)
        response = queryset.update(data, upsert=upsert)
        return response

    def remove(self, filters=None, queries=None):
        """Deletes all the documents matching query criteria.

        Deletes the model documents which match the filers criteria.

        Args:
            filters: array of data to find the matching document
            queries: dictionary of parameters to find the matching document.

        Returns:
            The number of documents deleted.
        """
        query = {}

        if queries:
            query = queries

        if filters:
            query = {
                "$and": filters
            }

        queryset = self.model.objects.raw(query)
        response = queryset.delete()
        return response

    def remove_one(self, queries=None):
        """Deletes a single document matching query criteria.

        Deletes the model document which match the filers criteria.

        Args:
            queries: dictionary of parameters to find the matching document.

        Returns:
            1 if the document is deleted, else 0.
        """
        query = {}

        if queries:
            query = queries

        try:
            model_object = self.model.objects.raw(query).first()
            model_object.delete()
            response = 1
        except self.model.DoesNotExist:
            response = 0

        return response
