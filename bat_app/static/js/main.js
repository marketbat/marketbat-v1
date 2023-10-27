

document.addEventListener("DOMContentLoaded", function() {

    // <<<<<<<<<<<<  Handle Showing and Hiding the Hero Containers >>>>>>>>>>>>>>>.
        const toggleTrendingButton = document.querySelector(".hero__body-carousel-trending-title");
        const trendingContainer = document.querySelector(".hero__body-carousel-trending-body");

        const toggleDropsButton = document.querySelector(".hero__body-carousel-drops-title");
        const dropsContainer = document.querySelector(".hero__body-carousel-drops-body");

        const toggleFavoritesButton = document.querySelector(".hero__body-carousel-favorites-title");
        const favoritesContainer = document.querySelector(".hero__body-carousel-favorites-body");


        toggleTrendingButton.addEventListener("click", function () {
        if (trendingContainer.classList.contains("active")) {
            $("#trending__carousel-collapse-down").show();
            $("#trending__carousel-collapse-up").hide();
            
            trendingContainer.classList.remove("active");
        } else {
            $("#trending__carousel-collapse-up").show();
            $("#trending__carousel-collapse-down").hide();
            trendingContainer.classList.add("active");
        }
        });

        toggleDropsButton.addEventListener("click", function () {
        if (dropsContainer.classList.contains("active")) {
            $("#drops__carousel-collapse-down").show();
            $("#drops__carousel-collapse-up").hide();
            
            dropsContainer.classList.remove("active");
        } else {
            $("#drops__carousel-collapse-up").show();
            $("#drops__carousel-collapse-down").hide();
            dropsContainer.classList.add("active");
        }
        });

        toggleFavoritesButton.addEventListener("click", function () {
        if (favoritesContainer.classList.contains("active")) {
            $("#favorites__carousel-collapse-down").show();
            $("#favorites__carousel-collapse-up").hide();
            
            favoritesContainer.classList.remove("active");
        } else {
            $("#favorites__carousel-collapse-up").show();
            $("#favorites__carousel-collapse-down").hide();
            favoritesContainer.classList.add("active");
        }
        });




    // <<<<<<<<<<<<<<<<<<<<< Handle Formatting Volume to thousands >>>>>>>>>>>>>>>>>>>>>>>>>
        var volumeElements = document.getElementsByClassName('formatted-volume');

            for (var i = 0; i < volumeElements.length; i++) {
                var volumeElement = volumeElements[i];
                var volumeValue = parseFloat(volumeElement.textContent);

                var formattedVolume = (volumeValue / 1000).toFixed(2) + 'K';
                volumeElement.textContent = formattedVolume;
        }



    //<<<<<<<<<<<<<<<<<<<< Handle Searching and Filtering of Assets. >>>>>>>>>>>>>>>>>>>>>>>>>
        

        function filterAssets() {
            var input = document.getElementById('search_assets');
            var filter = input.value.toUpperCase();
            var assetRows = document.querySelectorAll('.browse__body table tbody tr');
            var noAssetContainer = document.querySelector('.no__asset-found');

            assetRows.forEach(function(row) {
                var assetName = row.querySelector('.table__asset-name_symbol');
                var assetSymbol = row.querySelector('.table__asset-symbol');
                if (assetName.innerText.toUpperCase().indexOf(filter) > -1 || assetSymbol.innerText.toUpperCase().indexOf(filter) > -1) {
                    row.style.display = '';
                    noAssetContainer.style.display = 'none';
                } else {
                    row.style.display = 'none';
                    noAssetContainer.style.display = 'flex';
                }
            });
        }

        var searchInput = document.getElementById('search_assets');
        searchInput.addEventListener('input', filterAssets);





    // <<<<<<<<<<<<<<<<<<< Handle Filtering and Pagination Function of Market Bat Pro's Assets Table >>>>>>>>>>>>>>>>>>>>
        var selectedFilters = {
            'duration': 'twentyfour-hours',
            'sentiment': '', // Set the default sentiment filter ID if needed
            'category': 'All' // Set the default category filter ID if needed
        };

        function setFilter(filterType, filterId) {
            if (selectedFilters[filterType] === filterId) {
                delete selectedFilters[filterType];
            } else {
                selectedFilters[filterType] = filterId;
            }
            // Update UI to reflect the selected filters
            updateRowsPerPage();
            updateFilterUI();
            
        }

        function updateFilterUI() {
            // Remove active class from all filter buttons
            var filterButtons = document.querySelectorAll('.sentiment__filters-item-btn, .category__filters-item-btn');
            filterButtons.forEach(function(button) {
                button.classList.remove('active');
            });

            // Add active class to the selected filter buttons
            Object.values(selectedFilters).forEach(function(filterId) {
                var selectedButton = document.getElementById(filterId);
                if (selectedButton) {
                    selectedButton.classList.add('active');
                }
            });

        
            // Show/hide table rows based on the active sentiment and category filters
            var tableRows = document.querySelectorAll('.browse__body table tbody tr');
            tableRows.forEach(function(row) {
                var sentimentCell = row.querySelector('.sentiment-value[data-duration="' + selectedFilters['duration'] + '"]');
                var sentimentText = sentimentCell.querySelector('span').innerText;
                var sentimentFilter = selectedFilters['sentiment'];

                var categoryCell = row.querySelector('.category-value');
                var categoryText = categoryCell.querySelector('span').innerText;
                var categoryFilter = selectedFilters['category'];

                if ((sentimentText === sentimentFilter || !sentimentFilter) && (categoryText === categoryFilter || categoryFilter === 'All')) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });

            // Show/hide the "No Asset Found" container if no assets match the filters
            var noAssetContainer = document.querySelector('.no__asset-found');
            var tableRows = document.querySelectorAll('.browse__body table tbody tr');
            var visibleRows = Array.from(tableRows).filter(function(row) {
                var sentimentCell = row.querySelector('.sentiment-value[data-duration="' + selectedFilters['duration'] + '"]');
                var sentimentText = sentimentCell.querySelector('span').innerText;
                var sentimentFilter = selectedFilters['sentiment'];

                var categoryCell = row.querySelector('.category-value');
                var categoryText = categoryCell.querySelector('span').innerText;
                var categoryFilter = selectedFilters['category'];

                return (sentimentText === sentimentFilter || !sentimentFilter) && (categoryText === categoryFilter || categoryFilter === 'All');
            });
            console.log("visible rows is", visibleRows)

            if (visibleRows.length > 0) {
                localStorage.setItem("rows", visibleRows.length)
                noAssetContainer.style.display = 'none';
            } else {
                noAssetContainer.style.display = 'flex';
            }
            
        }

        var currentPage = 1;
        var rowsPerPageSelect = document.getElementById("rowsPerPage");
        var prevPageBtn = document.getElementById("prevPageBtn");
        var nextPageBtn = document.getElementById("nextPageBtn");
        var pageNumbersElement = document.getElementById("pageNumbers");
        var tableBody = document.getElementById("tableBody");
        var rows = tableBody.rows;

        function showRows(startIndex, endIndex) {
            for (var i = 0; i < rows.length; i++) {
                if (i >= startIndex && i < endIndex) {
                    rows[i].style.display = "table-row";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }


        function updatePagination() {
                var rowsPerPage = parseInt(rowsPerPageSelect.value);
                var visibleRows = parseInt(localStorage.getItem('rows'));
                var totalPages = Math.ceil(visibleRows / rowsPerPage);

                // Validate current page
                if (currentPage < 1) {
                    currentPage = 1;
                } else if (currentPage > totalPages) {
                    currentPage = totalPages;
                }

                // Calculate start and end page numbers to display
                var startPage, endPage;
                if (totalPages <= 10) {
                    // If there are 10 or fewer total pages, display all page numbers
                    startPage = 1;
                    endPage = totalPages;
                } else {
                    // If there are more than 10 total pages, display a subset
                    if (currentPage <= 6) {
                        startPage = 1;
                        endPage = 10;
                    } else if (currentPage + 4 >= totalPages) {
                        startPage = totalPages - 9;
                        endPage = totalPages;
                    } else {
                        startPage = currentPage - 5;
                        endPage = currentPage + 4;
                    }
                }

                // Update current page display
                var pageNumbersHTML = "";
                for (var i = startPage; i <= endPage; i++) {
                    if (i === currentPage) {
                        pageNumbersHTML += '<span class="active-page">' + i + '</span>';
                    } else {
                        pageNumbersHTML += '<span onclick="goToPage(' + i + ')">' + i + '</span>';
                    }
                }
                pageNumbersElement.innerHTML = pageNumbersHTML;

                // Calculate start and end index of rows to display
                var startIndex = (currentPage - 1) * rowsPerPage;
                var endIndex = Math.min(startIndex + rowsPerPage, visibleRows);

                // Show the rows for the current page
                showRows(startIndex, endIndex);

                // Enable/disable previous/next buttons based on current page
                prevPageBtn.disabled = currentPage === 1;
                nextPageBtn.disabled = currentPage === totalPages;
            }


        function updateRowsPerPage() {
            currentPage = 1;
            updatePagination();
        }

        function previousPage() {
            if (currentPage > 1) {
                currentPage--;
                updatePagination();
            }
        }

        function nextPage() {
            var totalPages = Math.ceil(rows.length / parseInt(rowsPerPageSelect.value));
            if (currentPage < totalPages) {
                currentPage++;
                updatePagination();
            }
        }

        function goToPage(page) {
            currentPage = page;
            updatePagination();
        }

        // Initialize the pagination
       
        // Call updateFilterUI initially to reflect any pre-selected filters
        document.addEventListener('DOMContentLoaded', function() { 
            updateFilterUI();
            updateRowsPerPage();
        });
    



    // <<<<<<<<<<<<<<< Handle Displaying of FAQ Containers >>>>>>>>>>>>>>>>>>>>
    const faqItems = document.querySelectorAll('.faq__container-item');

        faqItems.forEach((item) => {
            item.addEventListener('click', () => {
                faqItems.forEach((otherItem) => {
                    if (item !== otherItem) {
                        otherItem.classList.remove('active');
                    }
                });
                item.classList.toggle('active');
            });
        });




    //<<<<<<<<<<<<<<<<<< Handle Formatting of Timestamp for Posts >>>>>>>>>>>>>>>>>>>>>>>>

    function updateRelativeTime() {
        const timeElements = document.querySelectorAll('.community-post-time');
        const now = Math.floor(Date.now() / 1000); // Current time in seconds

        timeElements.forEach((timeElement) => {
            const postTimestamp = parseInt(timeElement.getAttribute('data-post-timestamp'));
            const timeDifference = now - postTimestamp;

            if (timeDifference < 60) {
            // Less than a minute
            timeElement.textContent = timeDifference + 's';
            } else if (timeDifference < 3600) {
            // Less than an hour
            timeElement.textContent = Math.floor(timeDifference / 60) + 'm';
            } else if (timeDifference < 86400) {
            // Less than a day
            timeElement.textContent = Math.floor(timeDifference / 3600) + 'h';
            } else {
            // More than a day, show the full date
            const date = new Date(postTimestamp * 1000);
            const formattedDate = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
            });
            timeElement.textContent = formattedDate;
            }
        });
    }

    // Call the function initially to format existing timestamps
    updateRelativeTime();

    // You can also set an interval to periodically update the timestamps
    setInterval(updateRelativeTime, 60000); // Update every minute

    

});